import json
import sqlite3
from datetime import datetime
from typing import Dict, Iterable, List

from .logging_config import logger
from .db import transaction

UNIFIED_SCHEMA = """
CREATE TABLE IF NOT EXISTS unified_courses (
    course_id TEXT PRIMARY KEY,      -- 'source:source_course_id'
    source TEXT NOT NULL,            -- 'edx' | 'coursera' | 'nptel'
    source_course_id TEXT NOT NULL,
    title TEXT,
    description TEXT,
    url TEXT,
    provider TEXT,                   -- org/partner/institute
    instructors_json TEXT,           -- JSON array
    subject TEXT,
    level TEXT,
    language TEXT,
    duration_weeks INTEGER,
    tags_json TEXT,                  -- JSON array
    skills_json TEXT,                -- JSON array
    rating REAL,
    ratings_count INTEGER,
    popularity INTEGER,
    image_url TEXT,
    created_at TEXT,
    updated_at TEXT,
    extra_json TEXT                  -- misc source-specific dictionary
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_unified_source_pair
ON unified_courses(source, source_course_id);

CREATE INDEX IF NOT EXISTS idx_unified_title ON unified_courses(title);
CREATE INDEX IF NOT EXISTS idx_unified_subject ON unified_courses(subject);
CREATE INDEX IF NOT EXISTS idx_unified_level ON unified_courses(level);

CREATE TABLE IF NOT EXISTS source_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,         -- FK-ish to unified_courses.course_id
    source TEXT NOT NULL,
    source_course_id TEXT NOT NULL,
    raw_record_json TEXT,
    recorded_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_source_map_course ON source_map(course_id);
"""

INSERT_SQL = """
INSERT INTO unified_courses (
    course_id, source, source_course_id, title, description, url, provider,
    instructors_json, subject, level, language, duration_weeks,
    tags_json, skills_json, rating, ratings_count, popularity, image_url,
    created_at, updated_at, extra_json
) VALUES (
    ?,?,?,?,?,?,
    ?,?,?,?,?,
    ?,?,?,?, ?,?,?,
    ?,?,?
)
ON CONFLICT(course_id) DO UPDATE SET
    title=excluded.title,
    description=excluded.description,
    url=excluded.url,
    provider=excluded.provider,
    instructors_json=excluded.instructors_json,
    subject=excluded.subject,
    level=excluded.level,
    language=excluded.language,
    duration_weeks=excluded.duration_weeks,
    tags_json=excluded.tags_json,
    skills_json=excluded.skills_json,
    rating=excluded.rating,
    ratings_count=excluded.ratings_count,
    popularity=excluded.popularity,
    image_url=excluded.image_url,
    updated_at=excluded.updated_at,
    extra_json=excluded.extra_json
;
"""

INSERT_SOURCE_MAP_SQL = """
INSERT INTO source_map (course_id, source, source_course_id, raw_record_json, recorded_at)
VALUES (?, ?, ?, ?, ?);
"""

def ensure_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(UNIFIED_SCHEMA)
    conn.commit()

def _pack_record(rec: Dict) -> List:
    now = datetime.utcnow().isoformat()
    course_id = f"{rec['source']}:{rec['source_course_id']}"
    instructors_json = json.dumps(rec.get("instructors") or [], ensure_ascii=False)
    tags_json = json.dumps(rec.get("tags") or [], ensure_ascii=False)
    skills_json = json.dumps(rec.get("skills") or [], ensure_ascii=False)
    extra_json = json.dumps(rec.get("extra") or {}, ensure_ascii=False)

    return [
        course_id, rec.get("source"), rec.get("source_course_id"),
        rec.get("title"), rec.get("description"), rec.get("url"), rec.get("provider"),
        instructors_json, rec.get("subject"), rec.get("level"), rec.get("language"),
        rec.get("duration_weeks"),
        tags_json, skills_json, rec.get("rating"), rec.get("ratings_count"),
        rec.get("popularity"), rec.get("image_url"),
        now, now, extra_json
    ]

def bulk_upsert(conn: sqlite3.Connection, records: Iterable[Dict], batch_size: int = 500):
    """
    Upsert records in batches (transaction per batch).
    Also records the raw source row in source_map for traceability.
    """
    cur = conn.cursor()
    batch_params = []
    batch_source_map = []

    def flush():
        if not batch_params:
            return
        with transaction(conn):
            cur.executemany(INSERT_SQL, batch_params)
            cur.executemany(INSERT_SOURCE_MAP_SQL, batch_source_map)
        logger.info("Upserted %d records", len(batch_params))
        batch_params.clear()
        batch_source_map.clear()

    for rec in records:
        packed = _pack_record(rec)
        batch_params.append(packed)
        # store source_map with the raw normalized rec (not the original DB row)
        raw_json = json.dumps(rec, ensure_ascii=False)
        course_id = f"{rec['source']}:{rec['source_course_id']}"
        batch_source_map.append([course_id, rec.get("source"), rec.get("source_course_id"), raw_json, datetime.utcnow().isoformat()])

        if len(batch_params) >= batch_size:
            flush()

    flush()
