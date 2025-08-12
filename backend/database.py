import sqlite3
from datetime import datetime

DB_PATH = "sessions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_message(session_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, created_at, updated_at) VALUES (?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET updated_at=excluded.updated_at",
              (session_id, datetime.now(), datetime.now()))
    c.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (session_id, role, content, datetime.now()))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id=? ORDER BY timestamp", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]