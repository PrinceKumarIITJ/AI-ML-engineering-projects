import sqlite3
from pathlib import Path

db_path = Path('data/leads.sqlite')
if not db_path.exists():
    print("Database not found.")
else:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT city, source_platform, COUNT(*) FROM leads GROUP BY city, source_platform")
        rows = cursor.fetchall()
        print("Data Summary:")
        for row in rows:
            print(f"City: {row[0]}, Source: {row[1]}, Count: {row[2]}")
        
        cursor.execute("SELECT COUNT(*) FROM leads")
        total = cursor.fetchone()[0]
        print(f"\nTotal Records: {total}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
