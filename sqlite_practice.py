import sqlite3

DB_FILE = "test_events.db"

def init_test_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE,
    order_id TEXT,
    status TEXT,
    version INTEGER
    )
    """)
    conn.commit()
    conn.close()
    print("Database and table initialized successfully!")

def insert_and_select_event(event_id, order_id, status, version):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO events (event_id, order_id, status, version) VALUES (?, ?, ?, ?)",
            (event_id, order_id, status, version)
        )
        conn.commit()
        print(f"Successfully inserted: {event_id}")
    except sqlite3.IntegrityError:
        print(f"Duplicate caught! Event ID '{event_id}' already exists.")
    cursor.execute("SELECT event_id, order_id, status, version FROM events WHERE event_id = ?", (event_id,))
    row = cursor.fetchone()

    if row:
        print(f"Fetched from DB -> Event ID: {row[0]}, Order: {row[1]}, Status: {row[2]}, Version: {row[3]}")

    conn.close()

if __name__ == "__main__":
    init_test_db()
    insert_and_select_event("evt_101", "ord_500", "placed", 1)
    print("\n--- Testing Duplicate Prevention (S3) ---")
    insert_and_select_event("evt_101", "ord_500", "placed", 1)