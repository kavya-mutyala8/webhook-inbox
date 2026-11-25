import sqlite3

DB_FILE = "inbox.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL,
    source TEXT NOT NULL,
    received_at TEXT NOT NULL
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
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT event_id, order_id, status, version, source FROM events WHERE event_id = ?", (event_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def save_event_and_state(event_id, order_id, status, version, source, received_at):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO events (event_id, order_id, status, version, source, received_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event_id, order_id, status, version, source, received_at))

        cursor.execute("""INSERT INTO order_state (order_id, current_status, current_version)
               VALUES (?, ?, ?)
               ON CONFLICT(order_id) DO UPDATE SET
               current_status = excluded.current_status,
               current_version = excluded.current_version
               WHERE excluded.current_version > order_state.current_version""",
            (order_id, status, version))
        conn.commit()
        return True
    except  sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()