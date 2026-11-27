import sqlite3
import datetime

DB_FILE = "inbox.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    order_id TEXT NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL,
    source TEXT NOT NULL,
    event_timestamp TEXT NOT NULL,
    received_at TEXT NOT NULL,
    body_hash TEXT NOT NULL,
    receive_count INTEGER NOT NULL DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_state (
    order_id TEXT PRIMARY KEY,
    current_status TEXT NOT NULL,
    current_version INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS replay_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    who TEXT,
    when_timestamp TEXT NOT NULL,
    result TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Database 'inbox.db' initialized with 3 production tables.")

def get_event_by_id(event_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT event_id, order_id, status, version, source, body_hash, receive_count FROM events WHERE event_id = ?", (event_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def save_event_and_state(event_id, order_id, status, version, source, event_timestamp, body_hash):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        received_at = datetime.datetime.utcnow().isoformat()

        cursor.execute("""INSERT OR IGNORE INTO events 
               (event_id, order_id, status, version, source, event_timestamp, received_at, body_hash, receive_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (event_id, order_id, status, version, source, event_timestamp, received_at, body_hash))

        if cursor.rowcount == 1:

            cursor.execute("""INSERT INTO order_state (order_id, current_status, current_version)
                   VALUES (?, ?, ?)
                   ON CONFLICT(order_id) DO UPDATE SET
                   current_status = excluded.current_status,
                   current_version = excluded.current_version
                   WHERE excluded.current_version > order_state.current_version""",
                (order_id, status, version))
            conn.commit()
            return "success"
        else:
            cursor.execute(
                "UPDATE events SET receive_count = receive_count + 1 WHERE event_id = ?",
                (event_id,)
            )
            cursor.execute("SELECT body_hash FROM events WHERE event_id = ?", (event_id,))
            stored_hash = cursor.fetchone()[0]
            conn.commit()
    
            if stored_hash != body_hash:
                return "conflict"
            return "duplicate"
            
    except sqlite3.Error:
        conn.rollback()
        return "db_error"
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()