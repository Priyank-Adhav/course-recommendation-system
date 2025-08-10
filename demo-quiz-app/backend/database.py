import sqlite3
import os

DATABASE = 'quiz_system.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
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

def reset_db():
    """Reset the database by deleting the file and recreating it"""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print("🗑️ Existing database deleted")
    init_db()
    print("🆕 Fresh database created")

# add near init_db()
def ensure_password_column():
    conn = get_db_connection()
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(users)")]
    if "password_hash" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        conn.commit()
    conn.close()

if __name__ == '__main__':
    # Option to reset database
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_db()
    else:
        init_db()