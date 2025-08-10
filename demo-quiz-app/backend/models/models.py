from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- Users ----------------
def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def create_user_secure(name, email, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)
    """, (name, email, generate_password_hash(password)))
    conn.commit()
    conn.close()

def verify_user_credentials(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    ok = check_password_hash(user["password_hash"], password) if user["password_hash"] else False
    return user if ok else None

def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user

# ---------------- Categories ----------------
def create_category(unique_id, name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO categories (unique_id, category_name)
        VALUES (?, ?)
    """, (unique_id, name))
    conn.commit()
    conn.close()

def get_all_categories():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return rows

# ---------------- Quizzes ----------------
def create_quiz(title, category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO quizzes (title, category_id)
        VALUES (?, ?)
    """, (title, category_id))
    conn.commit()
    conn.close()

def get_all_quizzes():
    conn = get_db_connection()
    quizzes = conn.execute("""
        SELECT q.*, c.category_name
        FROM quizzes q
        LEFT JOIN categories c ON q.category_id = c.id
    """).fetchall()
    conn.close()
    return quizzes

# ---------------- Questions ----------------
def add_question(quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, teacher_id=None, label_id=None, unique_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, teacher_id, label_id, unique_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, teacher_id, label_id, unique_id))
    conn.commit()
    conn.close()

def get_questions_for_quiz(quiz_id):
    conn = get_db_connection()
    questions = conn.execute("""
        SELECT * FROM questions WHERE quiz_id = ?
    """, (quiz_id,)).fetchall()
    conn.close()
    return questions

def get_correct_answers(quiz_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, correct_option FROM questions WHERE quiz_id = ?
    """, (quiz_id,)).fetchall()
    conn.close()
    return {int(row["id"]): int(row["correct_option"]) for row in rows}

# ---------------- Results (overall attempt) ----------------
def save_result(user_id, quiz_id, total_questions, correct_questions, time_taken, score):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO results (user_id, quiz_id, total_questions, correct_questions, time_taken, score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, quiz_id, total_questions, correct_questions, time_taken, score))
    conn.commit()
    result_id = cur.lastrowid
    conn.close()
    return result_id

def get_results_for_user(user_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT r.*, q.title
        FROM results r
        LEFT JOIN quizzes q ON r.quiz_id = q.id
        WHERE r.user_id = ?
    """, (user_id,)).fetchall()
    conn.close()
    return rows

# ---------------- Result per question ----------------
def save_result_per_question(result_id, question_id, points, correct_ans, submitted_ans, time_taken):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO result_per_question (result_id, question_id, points, correct_ans, submitted_ans, time_taken)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (result_id, question_id, points, correct_ans, submitted_ans, time_taken))
    conn.commit()
    conn.close()

def get_result_details(result_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT rpq.*, q.question_text
        FROM result_per_question rpq
        LEFT JOIN questions q ON rpq.question_id = q.id
        WHERE rpq.result_id = ?
    """, (result_id,)).fetchall()
    conn.close()
    return rows

# ---------------- Utilities ----------------
def clear_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM result_per_question")
    cursor.execute("DELETE FROM results")
    cursor.execute("DELETE FROM questions")
    cursor.execute("DELETE FROM quizzes")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM users")  # add this
    cursor.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    conn.close()