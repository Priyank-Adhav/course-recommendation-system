# scraper/catalog_scraper.py
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from scraper.utils import extract_js_courses_array

BASE = "https://nptel.ac.in"
CATALOG_URL = f"{BASE}/courses"
DB_PATH = Path("courses.db")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CourseScraper/1.0)"}

def upsert_course(conn, data):
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO courses(course_id, title, institute, professor, content_type, discipline_id, current_run, self_paced, url, scraped, last_updated)
    VALUES(?,?,?,?,?,?,?,?,?,0,?)
    ON CONFLICT(course_id) DO UPDATE SET
      title=excluded.title,
      institute=excluded.institute,
      professor=excluded.professor,
      content_type=excluded.content_type,
      discipline_id=excluded.discipline_id,
      current_run=excluded.current_run,
      self_paced=excluded.self_paced,
      url=excluded.url,
      last_updated=excluded.last_updated
    """, (
        str(data.get("id")),
        data.get("title"),
        data.get("instituteName"),
        data.get("professor"),
        data.get("contentType"),
        str(data.get("disciplineId")),
        1 if data.get("currentRun") else 0,
        1 if data.get("selfPaced") else 0,
        f"{BASE}/courses/{data.get('id')}",
        datetime.utcnow().isoformat()
    ))
    conn.commit()

def run():
    print("Fetching catalog:", CATALOG_URL)
    resp = requests.get(CATALOG_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text
    courses = extract_js_courses_array(html)
    print("Found", len(courses), "courses in embedded JS")
    conn = sqlite3.connect(DB_PATH)
    for c in courses:
        try:
            upsert_course(conn, c)
        except Exception as e:
            print("Error saving course", c.get("id"), e)
    conn.close()
    print("Catalog saved to DB:", DB_PATH)

if __name__ == "__main__":
    run()
