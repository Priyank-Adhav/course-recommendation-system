import sqlite3
from datetime import datetime
from recommend import recommend  

DB_PATH = "/home/priyank/Downloads/course-recommendation-system/demo-quiz-app/backend/quiz_system.db"

def fetch_user_quiz_data(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = """
    SELECT 
        qz.id AS quiz_id,
        qz.title AS quiz_title,
        q.question_text,
        r.score,
        r.completed_at
    FROM results r
    JOIN quizzes qz ON r.quiz_id = qz.id
    JOIN result_per_question rpq ON r.id = rpq.result_id
    JOIN questions q ON rpq.question_id = q.id
    WHERE r.user_id = ?
    """
    cur.execute(query, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def compute_recency_weight(completed_at_str: str) -> float:
    try:
        completed_at = datetime.fromisoformat(completed_at_str)
    except Exception:
        return 1.0
    days = (datetime.now() - completed_at).days
    return 1 / (1 + days / 7)  # one week half-life


def build_queries(user_id: int):
    rows = fetch_user_quiz_data(user_id)

    weak_topics = []
    strong_topics = []
    interest_topics = []

    for quiz_id, title, question_text, score, completed_at in rows:
        recency_w = compute_recency_weight(completed_at)
        text_blob = f"{title} {question_text}"

        if score < 50:
            weak_topics.append((text_blob, recency_w))
        elif score > 80:
            strong_topics.append((text_blob, recency_w))
        interest_topics.append((text_blob, recency_w))

    def combine_text_weighted(pairs):
        combined = " ".join([text for text, _ in pairs])
        avg_weight = sum(w for _, w in pairs) / len(pairs) if pairs else 1
        return combined.strip(), avg_weight

    weak_query, weak_w = combine_text_weighted(weak_topics)
    strong_query, strong_w = combine_text_weighted(strong_topics)
    interest_query, interest_w = combine_text_weighted(interest_topics)

    return {
        "weak": (weak_query, weak_w),
        "strong": (strong_query, strong_w),
        "interest": (interest_query, interest_w),
    }


def generate_user_recommendations(user_id: int, top_k: int = 9):
    queries = build_queries(user_id)
    results = {}

    if queries["weak"][0]:
        recs = recommend(queries["weak"][0], top_k)
        for r in recs:
            r["score"] *= queries["weak"][1] * 1.2
        results["struggled"] = sorted(recs, key=lambda x: x["score"], reverse=True)

    if queries["strong"][0]:
        recs = recommend(queries["strong"][0], top_k)
        for r in recs:
            r["score"] *= queries["strong"][1] * 0.9
        results["strong"] = sorted(recs, key=lambda x: x["score"], reverse=True)

    if queries["interest"][0]:
        recs = recommend(queries["interest"][0], top_k)
        for r in recs:
            r["score"] *= queries["interest"][1]
        results["interest"] = sorted(recs, key=lambda x: x["score"], reverse=True)

    return results
