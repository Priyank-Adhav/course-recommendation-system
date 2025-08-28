import sqlite3
from unified_catalog.extractors import extract_coursera, extract_edx, extract_nptel

def _rowcount(gen):
    return sum(1 for _ in gen)

def test_extract_coursera_minimal(tmp_path):
    db = tmp_path / "c.db"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE coursera_courses (
            id TEXT PRIMARY KEY,
            name TEXT, url TEXT, product_type TEXT,
            partners_json TEXT, skills_json TEXT,
            rating REAL, num_ratings INTEGER,
            difficulty TEXT, duration TEXT, tagline TEXT, fetched_at TEXT
        )
    """)
    cur.execute("""INSERT INTO coursera_courses
        (id, name, url, product_type, partners_json, skills_json, rating, num_ratings, difficulty, duration, tagline, fetched_at)
        VALUES
        ('c1','Title','/course','course','["Partner"]','["Python","ML"]',4.6,123,'Beginner','6 weeks','Great course','2025-01-01')
    """)
    conn.commit()
    gen = list(extract_coursera(conn))
    assert len(gen) == 1
    rec = gen[0]
    assert rec["source"] == "coursera"
    assert rec["title"] == "Title"
    assert rec["skills"] == ["Python", "ML"]
    conn.close()

def test_extract_edx_minimal(tmp_path):
    db = tmp_path / "e.db"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE courses (
            id TEXT PRIMARY KEY,
            title TEXT, description TEXT, subject TEXT, level TEXT, language TEXT,
            weeks_to_complete INTEGER, availability TEXT, marketing_url TEXT, card_image_url TEXT
        )
    """)
    cur.execute("""CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id TEXT, tag TEXT)""")
    cur.execute("""CREATE TABLE skills (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id TEXT, skill TEXT, category TEXT, subcategory TEXT)""")
    cur.execute("""CREATE TABLE staff (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id TEXT, staff_key TEXT)""")
    cur.execute("""CREATE TABLE owners (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id TEXT, name TEXT)""")

    cur.execute("""INSERT INTO courses VALUES
        ('e1','EdX Title','Desc','CS','Introductory','English',8,'Available','http://x','http://i')
    """)
    cur.execute("""INSERT INTO tags(course_id, tag) VALUES ('e1','AI'), ('e1','ML')""")
    cur.execute("""INSERT INTO skills(course_id, skill, category, subcategory) VALUES ('e1','Python','Prog','Lang')""")
    cur.execute("""INSERT INTO staff(course_id, staff_key) VALUES ('e1','prof_x')""")
    cur.execute("""INSERT INTO owners(course_id, name) VALUES ('e1','MITx')""")
    conn.commit()

    gen = list(extract_edx(conn))
    assert len(gen) == 1
    rec = gen[0]
    assert rec["source"] == "edx"
    assert rec["title"] == "EdX Title"
    assert set(rec["tags"]) == {"AI","ML"}
    assert rec["provider"] == "MITx"
    conn.close()

def test_extract_nptel_minimal(tmp_path):
    db = tmp_path / "n.db"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE courses (
            course_id TEXT PRIMARY KEY,
            title TEXT, institute TEXT, professor TEXT, content_type TEXT,
            discipline_id TEXT, current_run INTEGER, self_paced INTEGER,
            url TEXT, scraped INTEGER, last_updated TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE course_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT, lesson_number INTEGER, lesson_title TEXT,
            concepts_json TEXT, raw_concepts_text TEXT, fetched_at TEXT
        )
    """)
    cur.execute("""INSERT INTO courses VALUES
        ('n1','NPTEL Course','IIT','Prof A','video','ME',1,1,'http://nptel',0,'2025-01-01')
    """)
    cur.execute("""INSERT INTO course_metadata (course_id, lesson_number, lesson_title, concepts_json, raw_concepts_text, fetched_at)
        VALUES ('n1',1,'L1','["thermodynamics","cycles"]','heat; work','2025-01-02')
    """)
    conn.commit()

    gen = list(extract_nptel(conn))
    assert len(gen) == 1
    rec = gen[0]
    assert rec["source"] == "nptel"
    assert rec["provider"] == "IIT"
    assert "thermodynamics" in rec["tags"]
    assert "heat" in rec["tags"]
    conn.close()
