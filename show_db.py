import sqlite3

def show_tables():
    conn = sqlite3.connect("inbox.db")
    cursor = conn.cursor()
    
    print("=== EVENTS TABLE ==Abu")
    cursor.execute("SELECT event_id, order_id, status, version, event_timestamp, received_at FROM events")
    for row in cursor.fetchall():
        print(row)
        
    print("\n=== ORDER STATE TABLE ===")
    cursor.execute("SELECT order_id, current_status, current_version FROM order_state")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    show_tables()