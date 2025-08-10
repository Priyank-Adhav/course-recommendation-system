import requests
import os
import json
import random
import time
from datetime import datetime

# Base URL for your Flask application
PORT = int(os.environ.get("PORT", "5000"))
BASE_URL = f"http://localhost:{PORT}"

def check_server():
    """Check if the Flask server is running"""
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

def seed_data():
    """
    Comprehensive seed data function that populates the quiz system with:
    - Users (students and teachers)
    - Categories
    - Quizzes
    - Questions with multiple choice options
    - Sample quiz results
    """
    print("🌱 Starting to seed quiz system data...")
    
    # Check if server is running
    if not check_server():
        print("❌ ERROR: Flask server is not running!")
        print("📋 Please start your Flask server first:")
        print("   1. Run: python app.py")
        print("   2. Wait for server to start")
        print("   3. Then run this seed script again")
        return False
    
    # Clear existing data first
    print("🧹 Clearing existing data...")
    try:
        response = requests.post(f"{BASE_URL}/clear_all")
        if response.status_code == 200:
            print("✅ Existing data cleared successfully")
        else:
            print("⚠️ Warning: Could not clear existing data")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Warning: Could not connect to clear data: {e}")

    # Users (students + teachers)# Users (students + teachers)
    users_data = [
        {"name": "Alice Johnson", "email": "alice.johnson@email.com"},
        {"name": "Bob Smith", "email": "bob.smith@email.com"},
        {"name": "Carol Davis", "email": "carol.davis@email.com"},
        {"name": "David Wilson", "email": "david.wilson@email.com"},
        {"name": "Emma Brown", "email": "emma.brown@email.com"},
        {"name": "Frank Miller", "email": "frank.miller@email.com"},
        {"name": "Grace Lee", "email": "grace.lee@email.com"},
        {"name": "Henry Taylor", "email": "henry.taylor@email.com"},
        {"name": "Ivy Chen", "email": "ivy.chen@email.com"},
        {"name": "Jack Anderson", "email": "jack.anderson@email.com"},
        # Teachers
        {"name": "Dr. Sarah Martinez", "email": "sarah.martinez@school.edu"},
        {"name": "Prof. Michael Thompson", "email": "michael.thompson@school.edu"},
        {"name": "Ms. Jennifer White", "email": "jennifer.white@school.edu"},
    ]
    
# 1. Create Users (via /auth/register)
    print("\n👥 Registering users...")
    uids: dict[str, int] = {}

    def register_user(name: str, email: str, password: str = "password123") -> int | None:
        try:
            r = requests.post(f"{BASE_URL}/auth/register",
                            json={"name": name, "email": email, "password": password},
                            timeout=10)
            if r.status_code in (200, 201):
                data = r.json()
                print(f"✅ Registered user: {name}")
                return int(data["user"]["id"])
            else:
                print(f"❌ Failed to register {name}: {r.status_code} {r.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error registering {name}: {e}")
            return None

    for user in users_data:
        uid = register_user(user["name"], user["email"])
        if uid:
            uids[user["email"]] = uid

    print(f"👥 Total registered: {len(uids)}")

    # Teacher IDs (from registered users)
    T_SARAH = uids.get("sarah.martinez@school.edu")
    T_MICHAEL = uids.get("michael.thompson@school.edu")
    T_JENNIFER = uids.get("jennifer.white@school.edu")

    # Convenience user IDs for sample results
    U_ALICE = uids.get("alice.johnson@email.com")
    U_BOB = uids.get("bob.smith@email.com")
    U_CAROL = uids.get("carol.davis@email.com")
    U_DAVID = uids.get("david.wilson@email.com")
    U_EMMA = uids.get("emma.brown@email.com")
    U_FRANK = uids.get("frank.miller@email.com")
    
    # 2. Create Categories
    print("\n📚 Creating categories...")
    categories_data = [
        {"unique_id": "MATH", "name": "Mathematics"},
        {"unique_id": "SCI", "name": "Science"},
        {"unique_id": "HIST", "name": "History"},
        {"unique_id": "LIT", "name": "Literature"},
        {"unique_id": "PROG", "name": "Programming"},
        {"unique_id": "GEOG", "name": "Geography"},
        {"unique_id": "CHEM", "name": "Chemistry"},
        {"unique_id": "PHYS", "name": "Physics"},
        {"unique_id": "BIO", "name": "Biology"},
        {"unique_id": "ART", "name": "Art History"},
    ]
    
    for category in categories_data:
        try:
            response = requests.post(f"{BASE_URL}/categories", json=category, timeout=10)
            if response.status_code == 201:
                print(f"✅ Created category: {category['name']}")
            else:
                print(f"❌ Failed to create category: {category['name']} - Status: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating category {category['name']}: {e}")
            return False
    
    # 3. Create Quizzes
    print("\n📝 Creating quizzes...")
    quizzes_data = [
        {"title": "Basic Algebra", "category_id": 1},
        {"title": "Geometry Fundamentals", "category_id": 1},
        {"title": "Introduction to Chemistry", "category_id": 7},
        {"title": "Periodic Table Basics", "category_id": 7},
        {"title": "World War II History", "category_id": 3},
        {"title": "Ancient Civilizations", "category_id": 3},
        {"title": "Python Basics", "category_id": 5},
        {"title": "Object-Oriented Programming", "category_id": 5},
        {"title": "Cell Biology", "category_id": 9},
        {"title": "Genetics Fundamentals", "category_id": 9},
        {"title": "Classical Physics", "category_id": 8},
        {"title": "Modern Physics", "category_id": 8},
        {"title": "World Geography", "category_id": 6},
        {"title": "Shakespeare's Works", "category_id": 4},
        {"title": "Renaissance Art", "category_id": 10},
    ]
    
    for quiz in quizzes_data:
        try:
            response = requests.post(f"{BASE_URL}/quizzes", json=quiz)
            if response.status_code == 201:
                print(f"✅ Created quiz: {quiz['title']}")
            else:
                print(f"❌ Failed to create quiz: {quiz['title']}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating quiz {quiz['title']}: {e}")
    
    # 4. Create Questions
    print("\n❓ Creating questions...")
    questions_data = [
        # Basic Algebra Questions (Quiz ID: 1)
        {
            "quiz_id": 1,
            "question_text": "What is the value of x in the equation: 2x + 5 = 15?",
            "options": ["5", "7", "10", "3"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "ALG001",
            "unique_id": "Q001"
        },
        {
            "quiz_id": 1,
            "question_text": "Simplify: 3x + 2x - 4x",
            "options": ["x", "5x", "9x", "-x"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "ALG002",
            "unique_id": "Q002"
        },
        {
            "quiz_id": 1,
            "question_text": "If y = 2x + 3, what is y when x = 4?",
            "options": ["11", "9", "8", "10"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "ALG003",
            "unique_id": "Q003"
        },
        
        # Geometry Questions (Quiz ID: 2)
        {
            "quiz_id": 2,
            "question_text": "What is the area of a rectangle with length 8 and width 5?",
            "options": ["40", "26", "13", "32"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "GEO001",
            "unique_id": "Q004"
        },
        {
            "quiz_id": 2,
            "question_text": "How many degrees are in a triangle?",
            "options": ["180", "90", "360", "270"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "GEO002",
            "unique_id": "Q005"
        },
        
        # Chemistry Questions (Quiz ID: 3)
        {
            "quiz_id": 3,
            "question_text": "What is the chemical symbol for water?",
            "options": ["H2O", "CO2", "NaCl", "O2"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "CHEM001",
            "unique_id": "Q006"
        },
        {
            "quiz_id": 3,
            "question_text": "What is the atomic number of carbon?",
            "options": ["6", "12", "8", "14"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "CHEM002",
            "unique_id": "Q007"
        },
        {
            "quiz_id": 3,
            "question_text": "Which gas makes up approximately 78% of Earth's atmosphere?",
            "options": ["Nitrogen", "Oxygen", "Carbon Dioxide", "Argon"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "CHEM003",
            "unique_id": "Q008"
        },
        
        # Periodic Table Questions (Quiz ID: 4)
        {
            "quiz_id": 4,
            "question_text": "What is the symbol for gold?",
            "options": ["Au", "Ag", "Go", "Gd"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "CHEM004",
            "unique_id": "Q009"
        },
        {
            "quiz_id": 4,
            "question_text": "Which element has the atomic number 1?",
            "options": ["Hydrogen", "Helium", "Lithium", "Carbon"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "CHEM005",
            "unique_id": "Q010"
        },
        
        # World War II Questions (Quiz ID: 5)
        {
            "quiz_id": 5,
            "question_text": "In which year did World War II end?",
            "options": ["1945", "1944", "1946", "1943"],
            "correct_option": 0,
            "teacher_id": T_JENNIFER,
            "label_id": "HIST001",
            "unique_id": "Q011"
        },
        {
            "quiz_id": 5,
            "question_text": "Which event brought the United States into World War II?",
            "options": ["Pearl Harbor attack", "D-Day invasion", "Battle of Britain", "Fall of France"],
            "correct_option": 0,
            "teacher_id": T_JENNIFER,
            "label_id": "HIST002",
            "unique_id": "Q012"
        },
        
        # Python Programming Questions (Quiz ID: 7)
        {
            "quiz_id": 7,
            "question_text": "Which of the following is used to define a function in Python?",
            "options": ["def", "function", "func", "define"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "PROG001",
            "unique_id": "Q013"
        },
        {
            "quiz_id": 7,
            "question_text": "What is the output of: print(2 ** 3)?",
            "options": ["8", "6", "9", "23"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "PROG002",
            "unique_id": "Q014"
        },
        {
            "quiz_id": 7,
            "question_text": "Which data type is used to store text in Python?",
            "options": ["str", "string", "text", "char"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "PROG003",
            "unique_id": "Q015"
        },
        
        # Object-Oriented Programming Questions (Quiz ID: 8)
        {
            "quiz_id": 8,
            "question_text": "What is a class in object-oriented programming?",
            "options": ["A blueprint for creating objects", "A type of loop", "A conditional statement", "A variable type"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "PROG004",
            "unique_id": "Q016"
        },
        {
            "quiz_id": 8,
            "question_text": "What is inheritance in OOP?",
            "options": ["A class can inherit properties from another class", "A way to hide data", "A type of polymorphism", "A method to create objects"],
            "correct_option": 0,
            "teacher_id": T_SARAH,
            "label_id": "PROG005",
            "unique_id": "Q017"
        },
        
        # Cell Biology Questions (Quiz ID: 9)
        {
            "quiz_id": 9,
            "question_text": "What is the powerhouse of the cell?",
            "options": ["Mitochondria", "Nucleus", "Ribosome", "Chloroplast"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "BIO001",
            "unique_id": "Q018"
        },
        {
            "quiz_id": 9,
            "question_text": "What contains the genetic material of a cell?",
            "options": ["Nucleus", "Cytoplasm", "Cell membrane", "Vacuole"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "BIO002",
            "unique_id": "Q019"
        },
        
        # Physics Questions (Quiz ID: 11)
        {
            "quiz_id": 11,
            "question_text": "What is the acceleration due to gravity on Earth?",
            "options": ["9.8 m/s²", "10 m/s²", "9.6 m/s²", "8.9 m/s²"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "PHYS001",
            "unique_id": "Q020"
        },
        {
            "quiz_id": 11,
            "question_text": "What is the unit of force?",
            "options": ["Newton", "Joule", "Watt", "Pascal"],
            "correct_option": 0,
            "teacher_id": T_MICHAEL,
            "label_id": "PHYS002",
            "unique_id": "Q021"
        },
    ]
    
    # Add questions in batch
    try:
        response = requests.post(f"{BASE_URL}/questions", json=questions_data)
        if response.status_code == 201:
            print(f"✅ Created {len(questions_data)} questions successfully")
        else:
            print(f"❌ Failed to create questions batch")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating questions batch: {e}")
    
    # 5. Create Sample Quiz Results
    print("\n📊 Creating sample quiz results...")
    
    # Generate some realistic quiz attempts
    sample_results = [
        # Alice takes Basic Algebra quiz
        {
            "quiz_id": 1,
            "user_id": U_ALICE,
            "answers": {"1": 0, "2": 0, "3": 0},  # All correct
            "times": {"1": 45, "2": 30, "3": 25},
            "time_taken": 100
        },
        # Bob takes Basic Algebra quiz
        {
            "quiz_id": 1,
            "user_id": U_BOB,
            "answers": {"1": 0, "2": 1, "3": 0},  # 2 out of 3 correct
            "times": {"1": 60, "2": 40, "3": 35},
            "time_taken": 135
        },
        # Carol takes Chemistry quiz
        {
            "quiz_id": 3,
            "user_id": U_CAROL,
            "answers": {"6": 0, "7": 0, "8": 0},  # All correct
            "times": {"6": 30, "7": 25, "8": 40},
            "time_taken": 95
        },
        # David takes Python Basics quiz
        {
            "quiz_id": 7,
            "user_id": U_DAVID,
            "answers": {"13": 0, "14": 0, "15": 0},  # All correct
            "times": {"13": 20, "14": 15, "15": 25},
            "time_taken": 60
        },
        # Emma takes Geometry quiz
        {
            "quiz_id": 2,
            "user_id": U_EMMA,
            "answers": {"4": 0, "5": 0},  # All correct
            "times": {"4": 35, "5": 20},
            "time_taken": 55
        },
        # Frank takes Chemistry quiz with some wrong answers
        {
            "quiz_id": 3,
            "user_id": U_FRANK,
            "answers": {"6": 0, "7": 1, "8": 0},  # 2 out of 3 correct
            "times": {"6": 25, "7": 45, "8": 30},
            "time_taken": 100
        },
    ]
    
    for result in sample_results:
        try:
            response = requests.post(f"{BASE_URL}/submit", json=result)
            if response.status_code == 200:
                result_data = response.json()
                print(f"✅ Created quiz result: User {result['user_id']} scored {result_data['score']}/{result_data['total']}")
            else:
                print(f"❌ Failed to create result for user {result['user_id']}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating result for user {result['user_id']}: {e}")
    
    print("\n🎉 Seed data creation completed!")
    print("\n📈 Summary:")
    print(f"   👥 Users: {len(users_data)}")
    print(f"   📚 Categories: {len(categories_data)}")
    print(f"   📝 Quizzes: {len(quizzes_data)}")
    print(f"   ❓ Questions: {len(questions_data)}")
    print(f"   📊 Sample Results: {len(sample_results)}")
    
    # Display some useful endpoints to test
    print("\n🔗 Useful endpoints to test:")
    print(f"   GET {BASE_URL}/categories - View all categories")
    print(f"   GET {BASE_URL}/quizzes - View all quizzes")
    print(f"   GET {BASE_URL}/questions/1 - View questions for quiz 1")
    print(f"   GET {BASE_URL}/results/1 - View results for user 1")

def verify_data():
    """
    Verify that the seed data was created successfully
    """
    print("\n🔍 Verifying seed data...")
    
    endpoints_to_check = [
        ("/categories", "Categories"),
        ("/quizzes", "Quizzes"),
        ("/questions/1", "Questions for Quiz 1"),
        ("/results/1", "Results for User 1"),
    ]
    
    for endpoint, description in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print(f"✅ {description}: {count} items found")
            else:
                print(f"❌ {description}: Failed to retrieve (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Connection error - {e}")

if __name__ == "__main__":
    print("🚀 Quiz System Seed Data Generator")
    print("=" * 50)
    
    # Run the seed data function
    seed_data()
    
    # Optional: Verify the data was created
    verify_data()
    
    print("\n✨ All done! Your quiz system is now populated with sample data.")