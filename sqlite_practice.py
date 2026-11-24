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

def insert_events_for_demo():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO events (event_id, order_id, status, version) VALUES (?, ?, ?, ?)", ("evt_101", "ord_500", "placed", 1))
        cursor.execute("INSERT OR IGNORE INTO events (event_id, order_id, status, version) VALUES (?, ?, ?, ?)", ("evt_102", "ord_501", "paid", 1))
        conn.commit()
    finally:
        conn.close()

def safe_search_for_demo(user_input):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT event_id, order_id FROM events WHERE event_id = ?", (user_input,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def unsafe_search_for_demo(user_input):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        query = f"SELECT event_id, order_id FROM events WHERE event_id = '{user_input}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def failed_query_with_finally():
    print("\n--- S5: Testing finally block on error path ---")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM no_such_table")
    except sqlite3.Error as e:
        print("Database error occurred:", e)
    finally:
        conn.close()
        print("Database error path: connection successfully closed in 'finally' block.")


if __name__ == "__main__":
    init_test_db()
    insert_events_for_demo()
    
    print("\n================ S4 COMPARISON TESTS ================")
    
    payload_or = "x' OR '1'='1"
    print(f"Testing input: {payload_or}")
    print("Safe (?) result   :", safe_search_for_demo(payload_or))
    print("Unsafe (glued) res:", unsafe_search_for_demo(payload_or))
    
    payload_drop = "'; DROP TABLE events; --"
    print(f"\nTesting input: {payload_drop}")
    print("Unsafe (glued) res:", unsafe_search_for_demo(payload_drop))
    print("Safe (?) result   :", safe_search_for_demo(payload_drop))
    
    failed_query_with_finally()