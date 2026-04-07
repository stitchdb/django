import json
import threading
import requests

try:
    import websocket
    _ws_available = True
except ImportError:
    _ws_available = False


class StitchDBClient:
    """
    StitchDB client.

    Uses WebSocket for queries (1 connection, $0.019/M cost).
    Falls back to HTTP if WebSocket unavailable or fails.
    """

    def __init__(self, url, api_key):
        self.url = url.rstrip("/")
        self.ws_url = self.url.replace("https://", "wss://").replace("http://", "ws://")
        self.api_key = api_key
        self._ws = None
        self._ws_failed = False
        self._msg_id = 0
        self._pending = {}
        self._lock = threading.Lock()
        self._session = None

    # ---- WebSocket ----

    def _connect_ws(self):
        if self._ws and self._ws.connected:
            return True
        if self._ws_failed or not _ws_available:
            return False
        try:
            ws = websocket.WebSocket()
            ws.settimeout(30)
            ws.connect(
                f"{self.ws_url}/ws/query?key={self.api_key}",
                header={"Authorization": f"Bearer {self.api_key}"},
            )
            self._ws = ws
            return True
        except Exception:
            self._ws_failed = True
            return False

    def _ws_send(self, action, data):
        with self._lock:
            self._msg_id += 1
            msg_id = str(self._msg_id)

        msg = {"id": msg_id, "action": action, **data}
        try:
            self._ws.send(json.dumps(msg))
            raw = self._ws.recv()
            resp = json.loads(raw)
            if "error" in resp:
                raise Exception(f"StitchDB: {resp['error']}")
            return resp
        except Exception as e:
            self._ws_failed = True
            if self._ws:
                try:
                    self._ws.close()
                except Exception:
                    pass
                self._ws = None
            if "StitchDB:" in str(e):
                raise
            return self._http_post(action, data)

    # ---- HTTP fallback ----

    def _get_session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    def _http_post(self, action, data):
        session = self._get_session()
        if action == "batch":
            path = "/v1/batch"
            body = {"queries": data["queries"]}
        elif action == "exec":
            path = "/v1/exec"
            body = {"sql": data["sql"]}
        else:
            path = "/v1/query"
            body = {"sql": data["sql"]}
            if data.get("params"):
                body["params"] = list(data["params"])

        resp = session.post(f"{self.url}{path}", json=body)
        result = resp.json()
        if "error" in result:
            raise Exception(f"StitchDB: {result['error']}")
        return result

    # ---- Public API ----

    def _send(self, action, data):
        if not self._ws_failed and _ws_available:
            if self._connect_ws():
                return self._ws_send(action, data)
        return self._http_post(action, data)

    def query(self, sql, params=None):
        data = {"sql": sql}
        if params:
            data["params"] = list(params)
        return self._send("query", data)

    def execute(self, sql, params=None):
        return self.query(sql, params)

    def batch(self, queries):
        """Send multiple queries in one request.
        queries: list of {"sql": str, "params": list} dicts
        """
        return self._send("batch", {"queries": queries})

    def close(self):
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None
        if self._session:
            self._session.close()
            self._session = None
