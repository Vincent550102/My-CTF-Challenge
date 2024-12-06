import sqlite3
from contextlib import contextmanager
import hashlib
import random
import string


class Database:
    def __init__(self, db_name="notes.db"):
        self.db_name = db_name
        self.init_db()

    def generate_note_id(self):
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        hash_object = hashlib.sha256(random_str.encode())
        return hash_object.hexdigest()[:32]

    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_db() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def create_note(self, session_id, content):
        with self.get_db() as conn:
            c = conn.cursor()
            while True:
                note_id = self.generate_note_id()
                try:
                    c.execute(
                        """
                        INSERT INTO notes (note_id, session_id, content)
                        VALUES (?, ?, ?)
                    """,
                        (note_id, session_id, content),
                    )
                    conn.commit()
                    return note_id
                except sqlite3.IntegrityError:
                    continue

    def get_user_notes(self, session_id):
        with self.get_db() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT note_id, content, created_at
                FROM notes
                WHERE session_id = ?
                ORDER BY created_at DESC
            """,
                (session_id,),
            )
            return c.fetchall()

    def get_note_by_id(self, note_id):
        with self.get_db() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT * FROM notes
                WHERE note_id = ?
            """,
                (note_id,),
            )
            return c.fetchone()
