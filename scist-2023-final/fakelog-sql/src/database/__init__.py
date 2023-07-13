import sqlite3
import json


class Database():
    def __init__(self):
        self.conn = sqlite3.connect(
            'database/sqlite.db', check_same_thread=False)
        self.conn.execute('DROP TABLE IF EXISTS fakelog')
        self.conn.commit()
        self.cur = self.conn.cursor()
        sql_inits = open('database/init.sql', 'r').read()
        for sql_init in sql_inits.split(';'):
            self.conn.executescript(sql_init)
            self.conn.commit()

    def get_fakelog(self, log_id):
        try:
            cursor = self.conn.execute(
                f"SELECT * FROM fakelog WHERE id = {log_id}")
            fakelogs = cursor.fetchall()
            return fakelogs
        except Exception as e:
            return str(e)
