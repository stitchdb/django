from django.db.backends.sqlite3.features import DatabaseFeatures as SQLiteFeatures


class DatabaseFeatures(SQLiteFeatures):
    supports_transactions = False
    supports_atomic_references_rename = False
    can_clone_databases = False
    supports_json_field = False
