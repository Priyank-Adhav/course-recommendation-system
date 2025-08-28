# scraper/course_scraper.py
import sqlite3
import time
import re
import json
import json5
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scraper.utils import split_concepts

# ---- config ----
DB_PATH = Path("courses.db")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CourseScraper/1.0)"}
RATE_LIMIT_SECONDS = 0.5  # be polite
CONCURRENCY_LIMIT = 8

# ---- logging ----
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---- HTTP session with retries (connection pooling + robustness) ----
def make_session(retries=3, backoff=0.5, status_forcelist=(429, 500, 502, 503, 504)):
    s = requests.Session()
    retries_cfg = Retry(total=retries, backoff_factor=backoff, status_forcelist=status_forcelist, allowed_methods=frozenset(["GET","POST"]))
    s.mount("https://", HTTPAdapter(max_retries=retries_cfg))
    s.mount("http://", HTTPAdapter(max_retries=retries_cfg))
    s.headers.update(HEADERS)
    return s

# ---- DB helpers ----
def get_unscraped_courses(conn, limit=2500):
    cur = conn.cursor()
    cur.execute("SELECT course_id, url FROM courses WHERE scraped=0 LIMIT ?", (limit,))
    return cur.fetchall()

def mark_course_scraped(conn, course_id):
    cur = conn.cursor()
    cur.execute("UPDATE courses SET scraped=1, last_updated=? WHERE course_id=?", (datetime.utcnow().isoformat(), course_id))
    conn.commit()

def insert_metadata_bulk(conn, rows):
    """
    rows: list of tuples => (course_id, lesson_number, lesson_title, concepts_json, raw_concepts_text, fetched_at)
    Performs a single executemany for efficiency.
    """
    if not rows:
        return
    cur = conn.cursor()
    cur.executemany("""
    INSERT INTO course_metadata(course_id, lesson_number, lesson_title, concepts_json, raw_concepts_text, fetched_at)
    VALUES(?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---- JS extraction helper (supports object {..} or array [..]) ----
def _extract_js_value(html, key):
    """
    Find the JavaScript value assigned to `key:` and return the text for that value.
    Supports object ({...}) or array ([...]) by bracket-matching.
    Returns None if not found.
    """
    idx = html.find(f"{key}:")
    if idx == -1:
        return None
    # find the first bracket after the key (either { or [)
    m = re.search(rf"{re.escape(key)}\s*:\s*([\[\{{])", html[idx:])
    if not m:
        return None
    start_char = m.group(1)
    start = idx + m.start(1)
    # bracket matching
    depth = 0
    end = start
    open_ch = start_char
    close_ch = {"{":"}", "[":"]"}[open_ch]
    for i in range(start, len(html)):
        ch = html[i]
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                end = i
                break
    if end <= start:
        return None
    return html[start:end+1]

# ---- main parser ----
def parse_course_page(html):
    """
    Parse lessons + per-lesson concepts (preferred: from embedded JS `courseOutline`).
    Returns:
        lesson_titles: list[str]
        concepts_list: list[str]  # per-lesson raw concepts string
    """
    # try embedded JS (key: courseOutline)
    obj_text = _extract_js_value(html, "courseOutline")
    if obj_text:
        try:
            parsed = json5.loads(obj_text)
            units = parsed.get("units") or []
            lesson_titles = []
            concepts_list = []
            for unit in units:
                lessons = unit.get("lessons") or []
                for lesson in lessons:
                    name = lesson.get("name") or lesson.get("title") or ""
                    concepts_raw = lesson.get("concepts_covered") or lesson.get("concepts") or ""
                    # sometimes concepts_raw might be a list
                    if isinstance(concepts_raw, list):
                        concepts_raw = "; ".join([str(x) for x in concepts_raw])
                    lesson_titles.append(name.strip())
                    concepts_list.append(concepts_raw.strip() if isinstance(concepts_raw, str) else "")
            if lesson_titles:
                return lesson_titles, concepts_list
        except Exception as e:
            logger.debug("json5 parse error for embedded JS: %s", e)

    # fallback: parse rendered HTML
    soup = BeautifulSoup(html, "lxml")
    lesson_nodes = soup.select("ul.lessons-list li.lesson")
    lesson_titles = [ln.get_text(strip=True) for ln in lesson_nodes] if lesson_nodes else []

    # global Concepts Covered fallback (single block)
    concepts_text = None
    for p in soup.select("p.mt-4"):
        b = p.find("b")
        if b and "Concepts Covered" in b.get_text():
            full = p.get_text(separator=" ", strip=True)
            concepts_text = full.split("Concepts Covered:")[-1].strip()
            break

    if lesson_titles:
        if concepts_text:
            concepts_list = [concepts_text] * len(lesson_titles)
        else:
            concepts_list = [""] * len(lesson_titles)
        return lesson_titles, concepts_list

    return [], []

# ---- runner ----
def run(limit=2500):
    session = make_session()
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = get_unscraped_courses(conn, limit=limit)
        if not rows:
            logger.info("No unscraped courses found.")
            return

        for course_id, url in rows:
            try:
                logger.info("Fetching: %s %s", course_id, url)
                resp = session.get(url, timeout=30)
                if resp.status_code != 200:
                    logger.warning("HTTP %s skipping %s", resp.status_code, url)
                    continue

                lesson_titles, concepts_list = parse_course_page(resp.text)
                insert_rows = []
                fetched_at = datetime.utcnow().isoformat()
                for i, lesson_title in enumerate(lesson_titles, start=1):
                    raw_concepts_text = concepts_list[i-1] if i-1 < len(concepts_list) else ""
                    # ensure raw_concepts_text is a string
                    if isinstance(raw_concepts_text, list):
                        raw_concepts_text = "; ".join(map(str, raw_concepts_text))
                    concepts = split_concepts(raw_concepts_text) if raw_concepts_text else []
                    insert_rows.append((
                        str(course_id),
                        i,
                        lesson_title,
                        json.dumps(concepts, ensure_ascii=False),
                        raw_concepts_text,
                        fetched_at
                    ))

                if insert_rows:
                    insert_metadata_bulk(conn, insert_rows)
                    mark_course_scraped(conn, str(course_id))
                logger.info("Saved %d lessons for %s", len(insert_rows), course_id)

                time.sleep(RATE_LIMIT_SECONDS)

            except Exception as e:
                logger.exception("Error for %s: %s", course_id, e)

    finally:
        conn.close()
        session.close()

def run_single(course_id, url):
    session = make_session()
    conn = sqlite3.connect(DB_PATH)
    try:
        logger.info("Fetching single course: %s %s", course_id, url)
        resp = session.get(url, timeout=30)
        if resp.status_code != 200:
            logger.warning("HTTP %s skipping %s", resp.status_code, url)
            return

        lesson_titles, concepts_list = parse_course_page(resp.text)
        if not lesson_titles:
            logger.info("No lessons found for %s", course_id)

        insert_rows = []
        fetched_at = datetime.utcnow().isoformat()
        for i, lesson_title in enumerate(lesson_titles, start=1):
            raw_concepts_text = concepts_list[i-1] if i-1 < len(concepts_list) else ""
            if isinstance(raw_concepts_text, list):
                raw_concepts_text = "; ".join(map(str, raw_concepts_text))
            concepts = split_concepts(raw_concepts_text) if raw_concepts_text else []
            insert_rows.append((
                str(course_id),
                i,
                lesson_title,
                json.dumps(concepts, ensure_ascii=False),
                raw_concepts_text,
                fetched_at
            ))

        if insert_rows:
            insert_metadata_bulk(conn, insert_rows)
            mark_course_scraped(conn, str(course_id))
        logger.info("Saved %d lessons for %s", len(insert_rows), course_id)

    except Exception as e:
        logger.exception("Error for %s: %s", course_id, e)
    finally:
        conn.close()
        session.close()

# ---- quick test mode ----
if __name__ == "__main__":
    # uncomment one of the following as needed
    # run(limit=20)
    run_single(101101001, "https://nptel.ac.in/courses/101101001")
