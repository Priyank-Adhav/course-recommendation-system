from database import get_db_connection

# ---------------- Users ----------------
def create_user(name, email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user

# ---------------- Quizzes ----------------
def create_quiz(title):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO quizzes (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()

def get_all_quizzes():
    conn = get_db_connection()
    quizzes = conn.execute("SELECT * FROM quizzes").fetchall()
    conn.close()
    return quizzes

# ---------------- Questions ----------------
def add_question(quiz_id, text, a, b, c, d, correct):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (quiz_id, text, a, b, c, d, correct))
    conn.commit()
    conn.close()

def get_questions_for_quiz(quiz_id):
    conn = get_db_connection()
    questions = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    conn.close()
    return questions

# ---------------- Scores ----------------
def save_score(user_id, quiz_id, score):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO scores (user_id, quiz_id, score) VALUES (?, ?, ?)", (user_id, quiz_id, score))
    conn.commit()
    conn.close()

def get_scores_for_user(user_id):
    conn = get_db_connection()
    scores = conn.execute("SELECT * FROM scores WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return scores
