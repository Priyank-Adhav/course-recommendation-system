import os
import sqlite3
from datetime import datetime
from typing import Dict, Iterable, Iterator, List, Optional

from .logging_config import logger
from .transform import (
    parse_json_field,
    merge_unique_lists,
    normalize_level,
    parse_weeks,
)

# ---------- Helper: safe column access ----------
def _col(row: sqlite3.Row, name: str, fallback_cols: List[str] = None):
    if name in row.keys():
        return row[name]
    if fallback_cols:
        for alt in fallback_cols:
            if alt in row.keys():
                return row[alt]
    return None

# ---------- EDX ----------
def extract_edx(edx_conn: sqlite3.Connection) -> Iterator[Dict]:
    """
    Expects edX schema:
      courses(id PK, title, description, subject, level, language, weeks_to_complete, availability, marketing_url, card_image_url)
      skills(id, course_id, skill, category, subcategory)
      tags(id, course_id, tag)
      staff(id, course_id, staff_key)
      owners(id, course_id, name)
    """
    cur = edx_conn.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    # Preload skills/tags/staff/owners as dicts -> course_id : list
    skills_map: Dict[str, List[str]] = {}
    tags_map: Dict[str, List[str]] = {}
    staff_map: Dict[str, List[str]] = {}
    owner_map: Dict[str, List[str]] = {}

    for tbl, col, dest in [
        ("skills", "skill", skills_map),
        ("tags", "tag", tags_map),
        ("staff", "staff_key", staff_map),
        ("owners", "name", owner_map),
    ]:
        try:
            q = f"SELECT course_id, {col} FROM {tbl}"
            for row in cur.execute(q):
                cid = str(row[0])
                val = row[1]
                dest.setdefault(cid, []).append(val)
        except sqlite3.OperationalError:
            # Table might not exist
            logger.warning("edX table %s missing; continuing", tbl)

    for row in courses:
        cid = str(_col(row, "id"))
        title = _col(row, "title")
        desc = _col(row, "description")
        subject = _col(row, "subject")
        level = normalize_level(_col(row, "level"))
        language = _col(row, "language")
        weeks = parse_weeks(_col(row, "weeks_to_complete"))
        url = _col(row, "marketing_url")
        image = _col(row, "card_image_url")

        tags = merge_unique_lists(tags_map.get(cid, []))
        skills = merge_unique_lists(skills_map.get(cid, []))
        instructors = merge_unique_lists(staff_map.get(cid, []))
        providers = merge_unique_lists(owner_map.get(cid, []))

        rec = {
            "source": "edx",
            "source_course_id": cid,
            "title": title,
            "description": desc,
            "url": url,
            "provider": ", ".join(providers) if providers else None,
            "instructors": instructors,
            "subject": subject,
            "level": level,
            "language": language,
            "duration_weeks": weeks,
            "tags": tags,
            "skills": skills,
            "rating": None,
            "ratings_count": None,
            "popularity": None,
            "image_url": image,
            "extra": {
                "availability": _col(row, "availability"),
            },
        }
        yield rec

# ---------- Coursera ----------
def extract_coursera(coursera_conn: sqlite3.Connection) -> Iterator[Dict]:
    """
    Expects single table: coursera_courses with (at least)
      id (PK), name, url, product_type, partners_json, skills_json, rating,
      num_ratings OR numProductRatings, difficulty, duration/productDuration, tagline, fetched_at
    """
    cur = coursera_conn.cursor()
    try:
        cur.execute("SELECT * FROM coursera_courses")
    except sqlite3.OperationalError as e:
        logger.error("Coursera table 'coursera_courses' not found: %s", e)
        return

    for row in cur.fetchall():
        cid = str(_col(row, "id"))
        title = _col(row, "name")
        url = _col(row, "url")
        product_type = _col(row, "product_type")
        partners_json = _col(row, "partners_json")
        skills_json = _col(row, "skills_json")
        rating = _col(row, "rating")
        ratings_count = _col(row, "num_ratings", ["numProductRatings"])
        difficulty = normalize_level(_col(row, "difficulty"))
        duration_raw = _col(row, "duration", ["productDuration"])
        tagline = _col(row, "tagline")
        fetched_at = _col(row, "fetched_at")

        partners = parse_json_field(partners_json)
        provider = ", ".join(partners) if partners else None
        skills = parse_json_field(skills_json)

        weeks = parse_weeks(duration_raw)
        rec = {
            "source": "coursera",
            "source_course_id": cid,
            "title": title,
            "description": tagline,
            "url": url,
            "provider": provider,
            "instructors": [],
            "subject": None,
            "level": difficulty,
            "language": None,
            "duration_weeks": weeks,
            "tags": [],     # Coursera tags not scraped separately — keep empty
            "skills": skills,
            "rating": rating,
            "ratings_count": ratings_count,
            "popularity": None,
            "image_url": None,
            "extra": {
                "product_type": product_type,
                "fetched_at": fetched_at,
            },
        }
        yield rec

# ---------- NPTEL ----------
def extract_nptel(nptel_conn: sqlite3.Connection) -> Iterator[Dict]:
    """
    NPTEL schema:
      courses(course_id PK, title, institute, professor, content_type, discipline_id,
              current_run, self_paced, url, scraped, last_updated)
      course_metadata(id, course_id FK, lesson_number, lesson_title, concepts_json, raw_concepts_text, fetched_at)
    """
    cur = nptel_conn.cursor()
    try:
        cur.execute("SELECT * FROM courses")
    except sqlite3.OperationalError as e:
        logger.error("NPTEL table 'courses' not found: %s", e)
        return
    courses = cur.fetchall()

    # Collect concepts per course
    concepts: Dict[str, List[str]] = {}
    try:
        for row in cur.execute("SELECT course_id, concepts_json, raw_concepts_text FROM course_metadata"):
            cid = str(row["course_id"])
            tags = []
            if row["concepts_json"]:
                tags.extend(parse_json_field(row["concepts_json"]))
            if row["raw_concepts_text"]:
                tags.extend(parse_json_field(row["raw_concepts_text"]))
            if tags:
                concepts.setdefault(cid, []).extend(tags)
    except sqlite3.OperationalError:
        # course_metadata might be empty/missing
        pass

    for row in courses:
        cid = str(_col(row, "course_id"))
        title = _col(row, "title")
        institute = _col(row, "institute")
        professor = _col(row, "professor")
        url = _col(row, "url")
        provider = institute
        instructors = parse_json_field(professor) if professor else ([professor] if professor else [])

        tags = merge_unique_lists(concepts.get(cid, []))

        rec = {
            "source": "nptel",
            "source_course_id": cid,
            "title": title,
            "description": None,
            "url": url,
            "provider": provider,
            "instructors": instructors,
            "subject": _col(row, "discipline_id"),
            "level": None,
            "language": None,
            "duration_weeks": None,
            "tags": tags,
            "skills": [],  # not explicitly modeled
            "rating": None,
            "ratings_count": None,
            "popularity": None,
            "image_url": None,
            "extra": {
                "content_type": _col(row, "content_type"),
                "current_run": _col(row, "current_run"),
                "self_paced": _col(row, "self_paced"),
                "last_updated": _col(row, "last_updated"),
            },
        }
        yield rec

# ---------- Convenience dispatcher ----------
def get_extractor(source_name: str):
    name = source_name.lower()
    if name == "edx":
        return extract_edx
    if name == "coursera":
        return extract_coursera
    if name == "nptel":
        return extract_nptel
    raise ValueError(f"Unknown source: {source_name}")
