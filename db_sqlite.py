import logging
import sqlite3 as sl

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class DBSqlite:

    def __init__(self, db_name):

        self.db = None
        self.cursor = None
        self.db_name = db_name + ".db"
        log.info("A new instance of DBSqlite is created")
        log.debug("SQLite init. db filename: " + self.db_name)
        self.connect()

    def connect(self):
        try:
            log.info("Connecting to db " + self.db_name)
            self.db = sl.connect(self.db_name)
            self.cursor = self.db.cursor()
        except sl.Error:
            log.exception("sqlite exception at connect method")

    def disconnect(self):
        if self.db:
            log.info(f"Closing db '{self.db_name}'")
            self.db.close()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS codes(
        code TEXT PRIMARY KEY,
        description TEXT,
        expire_date TEXT
        )""")
        log.debug("Database created (if not exists)")

    def insert(self, item):
        self.cursor.execute("""INSERT OR IGNORE INTO codes VALUES(?,?,?) """,
                            item)
        self.cursor.commit()
        log.debug("Insert data to DB")

    def read(self):
        self.cursor.execute("""SELECT * FROM codes""")
        rows = self.cursor.fetchall()
        log.info("Read %s rows from DB", len(rows))
        log.debug(rows)
        return rows
