# db/init_db.py
import sqlite3
from pathlib import Path
from config import DB_PATH

def init_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS coursera_courses (
        id TEXT PRIMARY KEY,
        name TEXT,
        url TEXT,
        product_type TEXT,
        partners_json TEXT,
        skills_json TEXT,
        rating REAL,
        num_ratings INTEGER,
        difficulty TEXT,
        duration TEXT,
        tagline TEXT,
        fetched_at TEXT
    );
    """)

    # raw pages: add UNIQUE constraint to prevent duplicates
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coursera_raw_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT,
        cursor TEXT,
        page_index INTEGER,
        raw_json TEXT,
        fetched_at TEXT,
        UNIQUE (query_text, cursor, page_index)
    );
    """)

    # mapping table: records which query produced which course (many-to-many)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coursera_course_search (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id TEXT,
        query_text TEXT,
        page_index INTEGER,
        cursor TEXT,
        fetched_at TEXT,
        UNIQUE(course_id, query_text, page_index, cursor),
        FOREIGN KEY(course_id) REFERENCES coursera_courses(id)
    );
    """)

    # index to speed queries by query_text
    cur.execute("CREATE INDEX IF NOT EXISTS idx_course_search_query ON coursera_course_search(query_text);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_course_search_course ON coursera_course_search(course_id);")

    conn.commit()
    conn.close()
    print("Initialized DB at", Path(db_path).resolve())

if __name__ == "__main__":
    init_db()
