import sqlite3
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from config import TARGET_DB
from logging_config import logger

# Use TARGET_DB from config
DB_PATH = str(TARGET_DB)

# Download NLTK resources if not already available
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)

# Custom domain-specific stopwords (add more if needed)
CUSTOM_STOPWORDS = {
    "offered", "university", "system", "introduction", "course", "ready",
    "get", "learn", "study", "program", "career"
}


def normalize_text(text: str) -> str:
    """Lowercase, remove punctuation, tokenize, remove stopwords, lemmatize, deduplicate."""
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove non-alphanumeric chars
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Tokenize
    tokens = nltk.word_tokenize(text)

    # Remove stopwords + lemmatize
    stop_words = set(stopwords.words("english")) | CUSTOM_STOPWORDS
    lemmatizer = WordNetLemmatizer()
    cleaned_tokens = [
        lemmatizer.lemmatize(tok)
        for tok in tokens
        if tok not in stop_words and len(tok) > 2
    ]

    # Deduplicate + sort for consistency
    unique_tokens = sorted(set(cleaned_tokens))

    return " ".join(unique_tokens)


def build_course_tags(row: dict) -> str:
    """Merge subject, skills, tags, title, description into a single normalized field."""
    fields = []

    if row["subject"]:
        fields.append(row["subject"])

    if row["skills_json"]:
        try:
            skills = json.loads(row["skills_json"])
            if isinstance(skills, list):
                fields.extend(skills)
        except json.JSONDecodeError:
            pass

    if row["tags_json"]:
        try:
            tags = json.loads(row["tags_json"])
            if isinstance(tags, list):
                fields.extend(tags)
        except json.JSONDecodeError:
            pass

    if row["title"]:
        fields.append(row["title"])
    if row["description"]:
        fields.append(row["description"])

    combined = " ".join(fields)
    return normalize_text(combined)


def create_course_features():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS course_features (
            course_id TEXT PRIMARY KEY,
            title TEXT,
            tags TEXT,
            level TEXT,
            language TEXT
        )
    """)

    cur.execute("SELECT * FROM unified_courses")
    colnames = [desc[0] for desc in cur.description]

    rows = cur.fetchall()
    inserted = 0

    for row in rows:
        record = dict(zip(colnames, row))

        tags = build_course_tags(record)
        level = record["level"].lower() if record["level"] else ""
        language = record["language"].lower() if record["language"] else ""

        cur.execute("""
            INSERT OR REPLACE INTO course_features (course_id, title, tags, level, language)
            VALUES (?, ?, ?, ?, ?)
        """, (record["course_id"], record["title"], tags, level, language))
        
        inserted += 1

    conn.commit()
    conn.close()
    logger.info(f"Created course_features table with {inserted} rows.")


if __name__ == "__main__":
    create_course_features()
