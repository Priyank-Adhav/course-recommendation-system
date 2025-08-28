# db/init_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("courses.db")

def init_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # courses table: basic index & status
    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_id TEXT PRIMARY KEY,
        title TEXT,
        institute TEXT,
        professor TEXT,
        content_type TEXT,
        discipline_id TEXT,
        current_run INTEGER,
        self_paced INTEGER,
        url TEXT,
        scraped INTEGER DEFAULT 0,
        last_updated TEXT
    )
    """)
    # course_metadata: expanded details per course (syllabus, lessons, concepts)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS course_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id TEXT,
        lesson_number INTEGER,
        lesson_title TEXT,
        concepts_json TEXT,       -- JSON array string like ["thermodynamics","cycles"]
        raw_concepts_text TEXT,   -- raw string from the page
        fetched_at TEXT,
        FOREIGN KEY(course_id) REFERENCES courses(course_id)
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Initialized DB at", DB_PATH.resolve())
