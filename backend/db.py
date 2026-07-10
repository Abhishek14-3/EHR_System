import sqlite3
import os

# Store DB in the backend folder alongside app.py
DB_PATH = os.path.join(os.path.dirname(__file__), "ehr_users.db")

def init_db():
    """Initializes the SQLite database with the `users` table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Returns a fresh connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    init_db()
    print("Default users database initialized successfully at", DB_PATH)
