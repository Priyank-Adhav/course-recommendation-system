import sqlite3
import os
import hashlib
import time
from datetime import datetime, timedelta

# Database connection
DB_PATH = os.path.join(os.path.dirname(__file__), "quiz_system.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create categories table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_id TEXT UNIQUE NOT NULL,
            category_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create quizzes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Create questions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option INTEGER NOT NULL,
            teacher_id INTEGER,
            label_id TEXT,
            unique_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Create results table (overall quiz attempts)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_questions INTEGER NOT NULL,
            time_taken INTEGER DEFAULT 0,
            score REAL DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Create result_per_question table (individual question results)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS result_per_question (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            points INTEGER DEFAULT 0,
            correct_ans INTEGER,
            submitted_ans TEXT,
            time_taken INTEGER DEFAULT 0,
            FOREIGN KEY (result_id) REFERENCES results (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def clear_all_data():
    """Clear all existing data"""
    conn = get_db_connection()
    conn.execute("DELETE FROM result_per_question")
    conn.execute("DELETE FROM results")
    conn.execute("DELETE FROM questions")
    conn.execute("DELETE FROM quizzes")
    conn.execute("DELETE FROM categories")
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    print("🗑️  Cleared all existing data")

def create_user(name, email, password):
    """Create a user directly in database"""
    conn = get_db_connection()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, datetime.now())
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def seed_data():
    """Seed the database with sample data"""
    print("🌱 Starting to seed quiz system data...")
    
    # Initialize database tables
    init_db()
    
    # Clear existing data
    clear_all_data()
    
    # Create users
    users_data = [
        {"name": "John Doe", "email": "john@example.com", "password": "password123"},
        {"name": "Jane Smith", "email": "jane@example.com", "password": "password123"},
        {"name": "Bob Johnson", "email": "bob@example.com", "password": "password123"},
        {"name": "Alice Brown", "email": "alice@example.com", "password": "password123"},
        {"name": "Charlie Wilson", "email": "charlie@example.com", "password": "password123"}
    ]
    
    user_ids = []
    for user_data in users_data:
        try:
            user_id = create_user(user_data["name"], user_data["email"], user_data["password"])
            user_ids.append(user_id)
            print(f"✅ Created user: {user_data['name']} (ID: {user_id})")
        except Exception as e:
            print(f"❌ Failed to create user {user_data['name']}: {e}")
            user_ids.append(None)
    
    # Filter out None user IDs
    user_ids = [uid for uid in user_ids if uid is not None]
    
    if not user_ids:
        print("❌ No users created, cannot proceed")
        return
    
    # Create categories
    categories_data = [
        "Mathematics", "Science", "History", "Literature", "Geography",
        "Computer Science", "Art", "Music", "Sports", "Technology"
    ]
    
    conn = get_db_connection()
    category_ids = []
    for category_name in categories_data:
        cursor = conn.execute(
            "INSERT INTO categories (unique_id, category_name, created_at) VALUES (?, ?, ?)",
            (f"cat_{int(time.time())}_{len(category_ids)}", category_name, datetime.now())
        )
        category_ids.append(cursor.lastrowid)
    
    # Create quizzes
    quizzes_data = [
        {"title": "Basic Math", "category_id": category_ids[0]},
        {"title": "Algebra Fundamentals", "category_id": category_ids[0]},
        {"title": "Physics Basics", "category_id": category_ids[1]},
        {"title": "Chemistry 101", "category_id": category_ids[1]},
        {"title": "World History", "category_id": category_ids[2]},
        {"title": "American Literature", "category_id": category_ids[3]},
        {"title": "European Geography", "category_id": category_ids[4]},
        {"title": "Programming Basics", "category_id": category_ids[5]},
        {"title": "Art History", "category_id": category_ids[6]},
        {"title": "Classical Music", "category_id": category_ids[7]},
        {"title": "Football Rules", "category_id": category_ids[8]},
        {"title": "Web Development", "category_id": category_ids[9]},
        {"title": "Advanced Calculus", "category_id": category_ids[0]},
        {"title": "Organic Chemistry", "category_id": category_ids[1]},
        {"title": "Ancient Civilizations", "category_id": category_ids[2]}
    ]
    
    quiz_ids = []
    for quiz_data in quizzes_data:
        cursor = conn.execute(
            "INSERT INTO quizzes (title, category_id, created_at) VALUES (?, ?, ?)",
            (quiz_data["title"], quiz_data["category_id"], datetime.now())
        )
        quiz_ids.append(cursor.lastrowid)
    
    # Create questions
    questions_data = [
        {"quiz_id": quiz_ids[0], "text": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "correct": 1, "teacher_id": user_ids[0]},
        {"quiz_id": quiz_ids[0], "text": "What is 5 × 3?", "options": ["12", "15", "18", "20"], "correct": 1, "teacher_id": user_ids[0]},
        {"quiz_id": quiz_ids[0], "text": "What is 10 ÷ 2?", "options": ["3", "4", "5", "6"], "correct": 2, "teacher_id": user_ids[0]},
        {"quiz_id": quiz_ids[1], "text": "Solve: x + 5 = 10", "options": ["3", "4", "5", "6"], "correct": 2, "teacher_id": user_ids[0]},
        {"quiz_id": quiz_ids[1], "text": "Solve: 2x = 8", "options": ["2", "3", "4", "5"], "correct": 2, "teacher_id": user_ids[0]},
        {"quiz_id": quiz_ids[2], "text": "What is gravity?", "options": ["A force", "A particle", "A wave", "A field"], "correct": 0, "teacher_id": user_ids[1]},
        {"quiz_id": quiz_ids[2], "text": "What is the SI unit of force?", "options": ["Joule", "Watt", "Newton", "Pascal"], "correct": 2, "teacher_id": user_ids[1]},
        {"quiz_id": quiz_ids[3], "text": "What is H2O?", "options": ["Carbon dioxide", "Water", "Oxygen", "Hydrogen"], "correct": 1, "teacher_id": user_ids[1]},
        {"quiz_id": quiz_ids[4], "text": "When did World War II end?", "options": ["1943", "1944", "1945", "1946"], "correct": 2, "teacher_id": user_ids[2]},
        {"quiz_id": quiz_ids[5], "text": "Who wrote 'To Kill a Mockingbird'?", "options": ["Mark Twain", "Harper Lee", "J.D. Salinger", "F. Scott Fitzgerald"], "correct": 1, "teacher_id": user_ids[2]},
        {"quiz_id": quiz_ids[6], "text": "What is the capital of France?", "options": ["London", "Berlin", "Madrid", "Paris"], "correct": 3, "teacher_id": user_ids[3]},
        {"quiz_id": quiz_ids[7], "text": "What is HTML?", "options": ["Programming language", "Markup language", "Database", "Framework"], "correct": 1, "teacher_id": user_ids[4]},
        {"quiz_id": quiz_ids[8], "text": "Who painted the Mona Lisa?", "options": ["Van Gogh", "Da Vinci", "Picasso", "Rembrandt"], "correct": 1, "teacher_id": user_ids[4]},
        {"quiz_id": quiz_ids[9], "text": "Who composed 'Symphony No. 9'?", "options": ["Mozart", "Beethoven", "Bach", "Chopin"], "correct": 1, "teacher_id": user_ids[4]},
        {"quiz_id": quiz_ids[10], "text": "How many players in a football team?", "options": ["9", "10", "11", "12"], "correct": 2, "teacher_id": user_ids[3]},
        {"quiz_id": quiz_ids[11], "text": "What is JavaScript?", "options": ["Markup language", "Programming language", "Database", "Framework"], "correct": 1, "teacher_id": user_ids[4]},
        {"quiz_id": quiz_ids[12], "text": "What is the derivative of x²?", "options": ["x", "2x", "x²", "2x²"], "correct": 1, "teacher_id": user_ids[0]},
        {"quiz_id": quiz_ids[13], "text": "What is the chemical formula for glucose?", "options": ["C6H12O6", "C12H22O11", "CH3COOH", "NaHCO3"], "correct": 0, "teacher_id": user_ids[1]},
        {"quiz_id": quiz_ids[14], "text": "Which civilization built the pyramids?", "options": ["Greeks", "Romans", "Egyptians", "Mayans"], "correct": 2, "teacher_id": user_ids[2]}
    ]
    
    for question_data in questions_data:
        conn.execute(
            """INSERT INTO questions 
               (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, teacher_id, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (question_data["quiz_id"], question_data["text"], 
             question_data["options"][0], question_data["options"][1], 
             question_data["options"][2], question_data["options"][3], 
             question_data["correct"], question_data["teacher_id"], datetime.now())
        )
    
    # Create sample results
    sample_results = [
        {"user_id": user_ids[0], "quiz_id": quiz_ids[0], "total": 3, "correct": 2, "time": 120},
        {"user_id": user_ids[1], "quiz_id": quiz_ids[1], "total": 2, "correct": 1, "time": 90},
        {"user_id": user_ids[2], "quiz_id": quiz_ids[2], "total": 2, "correct": 2, "time": 150},
        {"user_id": user_ids[3], "quiz_id": quiz_ids[3], "total": 1, "correct": 1, "time": 60},
        {"user_id": user_ids[4], "quiz_id": quiz_ids[4], "total": 1, "correct": 1, "time": 75},
        {"user_id": user_ids[0], "quiz_id": quiz_ids[5], "total": 1, "correct": 0, "time": 45}
    ]
    
    for result_data in sample_results:
        if result_data["user_id"] is not None:  # Only create results for valid users
            cursor = conn.execute(
                """INSERT INTO results 
                   (user_id, quiz_id, total_questions, correct_questions, time_taken, score, completed_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (result_data["user_id"], result_data["quiz_id"], 
                 result_data["total"], result_data["correct"], 
                 result_data["time"], 
                 (result_data["correct"] / result_data["total"]) * 100,
                 datetime.now() - timedelta(days=1))
            )
            
            # Create result details for each question
            result_id = cursor.lastrowid
            questions_for_quiz = [q for q in questions_data if q["quiz_id"] == result_data["quiz_id"]]
            
            for i, question in enumerate(questions_for_quiz[:result_data["total"]]):
                is_correct = i < result_data["correct"]
                conn.execute(
                    """INSERT INTO result_per_question 
                       (result_id, question_id, points, correct_ans, submitted_ans, time_taken) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (result_id, question["quiz_id"], 
                     1 if is_correct else 0, 
                     question["correct"], 
                     question["correct"] if is_correct else (question["correct"] + 1) % 4,
                     result_data["time"] // result_data["total"])
                )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Users: {len(user_ids)} created")
    print(f"✅ Categories: {len(category_ids)} created")
    print(f"✅ Quizzes: {len(quiz_ids)} created")
    print(f"✅ Questions: {len(questions_data)} created")
    print(f"✅ Sample Results: {len(sample_results)} created")
    
    print("✨ All done! Your quiz system is now populated with sample data.")

if __name__ == "__main__":
    seed_data()