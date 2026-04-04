"""
StitchDB database backend for Django.
Wraps the StitchDB HTTP API behind Django's database backend interface.
Uses SQLite-compatible SQL since StitchDB uses SQLite under the hood.
"""

from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper
from django.db.backends.sqlite3.base import Database
from .client import StitchDBClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor

import sqlite3
import json


class StitchDBCursorWrapper:
    """A cursor that sends queries to StitchDB's HTTP API."""

    def __init__(self, client):
        self.client = client
        self.description = None
        self._results = []
        self._rowcount = -1
        self.lastrowid = None
        self.arraysize = 1

    @property
    def rowcount(self):
        return self._rowcount

    def execute(self, sql, params=None):
        sql = str(sql).strip()
        if not sql:
            return

        # Convert Django's %s placeholders to ? for SQLite
        if params:
            sql = sql.replace("%s", "?")
            params = list(params)
        else:
            params = None

        try:
            result = self.client.query(sql, params)
            results = result.get("results", [])
            meta = result.get("meta", {})

            self.lastrowid = meta.get("last_row_id")
            self._rowcount = meta.get("rows_written", len(results))

            if results and len(results) > 0:
                columns = list(results[0].keys())
                self.description = [
                    (col, None, None, None, None, None, None) for col in columns
                ]
                self._results = [tuple(row.get(col) for col in columns) for row in results]
            else:
                self.description = None
                self._results = []
        except Exception as e:
            raise Exception(str(e))

    def executemany(self, sql, param_list):
        for params in param_list:
            self.execute(sql, params)

    def fetchone(self):
        if self._results:
            return self._results.pop(0)
        return None

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        results = self._results[:size]
        self._results = self._results[size:]
        return results

    def fetchall(self):
        results = self._results
        self._results = []
        return results

    def close(self):
        pass

    def __iter__(self):
        return iter(self._results)


class DatabaseWrapper(SQLiteDatabaseWrapper):
    vendor = "stitchdb"
    display_name = "StitchDB"

    # Use SQLite data types
    data_types = SQLiteDatabaseWrapper.data_types

    SchemaEditorClass = DatabaseSchemaEditor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self._stitchdb_client = None

    def get_stitchdb_client(self):
        if self._stitchdb_client is None:
            url = self.settings_dict.get("URL", "https://db.stitchdb.com")
            api_key = self.settings_dict.get("API_KEY", "")
            self._stitchdb_client = StitchDBClient(url, api_key)
        return self._stitchdb_client

    def get_connection_params(self):
        return {"database": ":memory:"}

    def get_new_connection(self, conn_params):
        # We need a real SQLite connection for Django's internals
        # (schema introspection, etc.) but all actual queries go through HTTP
        conn = Database.connect(":memory:")
        return conn

    def create_cursor(self, name=None):
        return StitchDBCursorWrapper(self.get_stitchdb_client())

    def _cursor(self):
        return self.create_cursor()

    def is_usable(self):
        return True

    def _set_autocommit(self, autocommit):
        pass

    def _start_transaction_under_autocommit(self):
        pass

    def _savepoint(self, sid):
        pass

    def _savepoint_rollback(self, sid):
        pass

    def _savepoint_commit(self, sid):
        pass

    def _commit(self):
        pass

    def _rollback(self):
        pass
