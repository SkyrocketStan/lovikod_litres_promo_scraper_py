import logging
import sqlite3 as sl

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class DBSqlite:

    def __init__(self, db_name):

        self.db = None
        self.db_name = db_name + ".db"
        log.info("A new instance of DBSqlite is created")
        log.debug("SQLite init. db filename: " + self.db_name)

    def connect(self):
        try:
            log.info("Connecting to db " + self.db_name)
            self.db = sl.connect(self.db_name)
        except sl.Error:
            log.exception("sqlite exception at connect method")

    def disconnect(self):
        if self.db:
            log.info(f"Closing db '{self.db_name}'")
            self.db.close()

# TODO: Create table
# TODO: Read data
# TODO: Update data
# TODO: Delete data
