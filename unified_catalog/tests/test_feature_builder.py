import sqlite3
import os
import pytest
from feature_builder import normalize_text, build_course_tags, create_course_features, DB_PATH

@pytest.fixture(scope="module")
def temp_db(tmp_path_factory):
    # Create temp DB
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE unified_courses (
            course_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            subject TEXT,
            level TEXT,
            language TEXT,
            tags_json TEXT,
            skills_json TEXT
        )
    """)

    cur.execute("""
        INSERT INTO unified_courses VALUES (
            'test:1',
            'Intro to AI',
            'This course teaches basics of artificial intelligence',
            'Computer Science',
            'Beginner',
            'English',
            '["ML", "AI"]',
            '["Python", "Neural Networks"]'
        )
    """)

    conn.commit()
    conn.close()
    return str(db_file)


def test_normalize_text():
    text = "This is a TEST!!!"
    result = normalize_text(text)
    assert "test" in result
    assert "this" not in result  # stopword removed


def test_build_course_tags():
    row = {
        "subject": "Data Science",
        "skills_json": '["Python", "Pandas"]',
        "tags_json": '["ML", "AI"]',
        "title": "Learn AI",
        "description": "Artificial intelligence basics"
    }
    tags = build_course_tags(row)
    assert "python" in tags
    assert "ai" in tags


def test_create_course_features(temp_db, monkeypatch):
    # Patch DB_PATH to use temp DB
    monkeypatch.setattr("feature_builder.DB_PATH", temp_db)

    create_course_features()

    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM course_features")
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 1
    assert "ai" in rows[0][2]  # tags field
