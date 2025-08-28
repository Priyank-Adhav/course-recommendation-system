import sqlite3

DB_PATH = "unified_courses.db"   # change if needed

def clean_non_english_records(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Drop rows where language is not 'English' and not NULL
    cur.execute("""
        DELETE FROM unified_courses
        WHERE language IS NOT NULL
          AND LOWER(language) != 'english';
    """)

    deleted = cur.rowcount
    conn.commit()
    conn.close()
    print(f"✅ Deleted {deleted} non-English records")

if __name__ == "__main__":
    clean_non_english_records()
