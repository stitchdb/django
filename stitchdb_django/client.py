import requests


class StitchDBClient:
    def __init__(self, url, api_key):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def query(self, sql, params=None):
        body = {"sql": sql}
        if params:
            body["params"] = list(params)
        resp = self.session.post(f"{self.url}/v1/query", json=body)
        data = resp.json()
        if "error" in data:
            raise Exception(f"StitchDB: {data['error']}")
        return data

    def execute(self, sql, params=None):
        return self.query(sql, params)
