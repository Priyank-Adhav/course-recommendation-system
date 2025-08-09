import sqlite3
import pandas as pd
import os

# Path to your SQLite DB
db_path = "quiz_system.db"

# Output folder for CSVs
output_folder = "db_exports"
os.makedirs(output_folder, exist_ok=True)

# Connect to DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    # Read table into DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

    # Save to CSV
    csv_path = os.path.join(output_folder, f"{table}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"Exported {table} → {csv_path}")

conn.close()
print("✅ All tables exported to CSV!")
