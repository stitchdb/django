from django.db.backends.sqlite3.creation import DatabaseCreation as SQLiteCreation


class DatabaseCreation(SQLiteCreation):
    def create_test_db(self, *args, **kwargs):
        pass

    def destroy_test_db(self, *args, **kwargs):
        pass
