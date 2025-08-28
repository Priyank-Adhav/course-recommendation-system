import requests
import sqlite3

# -----------------------------
# Algolia API config
# -----------------------------

url = "https://igsyv1z1xi-dsn.algolia.net/1/indexes/*/queries"

headers = {
    "X-Algolia-API-Key": "6658746ce52e30dacfdd8ba5f8e8cf18",
    "X-Algolia-Application-Id": "IGSYV1Z1XI",
    "Content-Type": "application/json",
}

subjects = [
    "Business & Management",
    "Computer Science",
    "Engineering",
    "Economics & Finance",
    "Social Sciences",
    "Data Analysis & Statistics",
    "Humanities",
    "Communication",
    "Science",
    "Environmental Studies",
    "Medicine",
    "Education & Teacher Training",
    "Health & Safety",
    "Biology & Life Sciences",
    "Art & Culture",
    "Math",
    "History",
    "Energy & Earth Sciences",
    "Law",
    "Design",
    "Physics",
    "Philosophy & Ethics",
    "Language",
    "Food & Nutrition",
    "Electronics",
    "Chemistry",
    "Architecture",
    "Ethics",
    "Literature",
    "Music",
    "Philanthropy",
]

# -----------------------------
# SQLite setup
# -----------------------------

conn = sqlite3.connect("courses.db")
cur = conn.cursor()

script = """
CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    subject TEXT,
    level TEXT,
    language TEXT,
    weeks_to_complete INTEGER,
    availability TEXT,
    marketing_url TEXT,
    card_image_url TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    skill TEXT,
    category TEXT,
    subcategory TEXT,
    UNIQUE(course_id, skill, category, subcategory) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    tag TEXT,
    UNIQUE(course_id, tag) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    staff_key TEXT,
    UNIQUE(course_id, staff_key) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    name TEXT,
    UNIQUE(course_id, name) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
"""

cur.executescript(script)

# -----------------------------
# Helper to insert one course
# -----------------------------


def insert_course(hit):
    cur.execute(
        """
        INSERT OR IGNORE INTO courses (
            id, title, description, subject, level,
            language, weeks_to_complete,
            availability, marketing_url, card_image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            hit.get("uuid"),
            hit.get("title"),
            hit.get("primary_description"),
            hit.get("subject")[0] if hit.get("subject") else None,
            hit.get("level")[0] if hit.get("level") else None,
            hit.get("language")[0] if hit.get("language") else None,
            hit.get("weeks_to_complete"),
            hit.get("availability")[0] if hit.get("availability") else None,
            hit.get("marketing_url"),
            hit.get("card_image_url"),
        ),
    )

    # Skills
    for s in hit.get("skills", []):
        if isinstance(s, dict):
            skill_name = s.get("skill")
            category = s.get("category")
            subcategory = s.get("subcategory")
        else:
            skill_name = s
            category = None
            subcategory = None

        cur.execute(
            """
            INSERT INTO skills (course_id, skill, category, subcategory)
            VALUES (?, ?, ?, ?)
            """,
            (hit.get("uuid"), skill_name, category, subcategory),
        )

    # Tags
    for t in hit.get("tags", []):
        cur.execute(
            "INSERT INTO tags (course_id, tag) VALUES (?, ?)", (hit.get("uuid"), t)
        )

    # Staff
    for st in hit.get("staff", []):
        cur.execute(
            "INSERT INTO staff (course_id, staff_key) VALUES (?, ?)",
            (hit.get("uuid"), st),
        )

    # Owners
    for o in hit.get("owners", []):
        cur.execute(
            "INSERT INTO owners (course_id, name) VALUES (?, ?)",
            (hit.get("uuid"), o.get("name")),
        )


# -----------------------------
# Crawl loop
# -----------------------------

for subject in subjects:
    print(f"Fetching subject: {subject}")
    page = 0

    while True:
        payload = {
            "requests": [
                {
                    "indexName": "product",
                    "filters": f'product:"Course" AND subject:"{subject}"',
                    "hitsPerPage": 100,
                    "page": page,
                }
            ]
        }

        r = requests.post(url, headers=headers, json=payload)
        data = r.json()["results"][0]

        hits = data["hits"]
        if not hits:
            break

        for h in hits:
            insert_course(h)

        conn.commit()
        print(f"  Page {page+1}/{data['nbPages']} → stored {len(hits)} courses")

        if page >= data["nbPages"] - 1:
            break
        page += 1

print("All courses saved to SQLite.")
conn.close()
