# seed_data.py
from models import models

def seed_quizzes():
    quizzes = [
        {
            "title": "Basic Math Quiz",
            "questions": [
                ("What is 2 + 2?", ["3", "4", "5", "6"], 1),
                ("What is 5 × 3?", ["8", "15", "10", "20"], 1),
                ("Square root of 16?", ["2", "4", "6", "8"], 1),
                ("What is 12 - 7?", ["4", "5", "6", "7"], 1),
                ("10 ÷ 2 = ?", ["2", "4", "5", "6"], 2)
            ]
        },
        {
            "title": "Basic Science Quiz",
            "questions": [
                ("What planet is known as the Red Planet?", ["Earth", "Mars", "Jupiter", "Saturn"], 1),
                ("Water freezes at what temperature (°C)?", ["0", "100", "50", "-1"], 0),
                ("What gas do plants produce during photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], 0),
                ("The powerhouse of the cell is?", ["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"], 2),
                ("Which organ pumps blood?", ["Lungs", "Heart", "Brain", "Liver"], 1)
            ]
        },
        {
            "title": "World History Quiz",
            "questions": [
                ("Who was the first President of the USA?", ["Abraham Lincoln", "George Washington", "John Adams", "Thomas Jefferson"], 1),
                ("World War II ended in?", ["1940", "1945", "1950", "1939"], 1),
                ("Who discovered America?", ["Christopher Columbus", "Marco Polo", "Vasco da Gama", "Magellan"], 0),
                ("The Roman Empire fell in?", ["476 AD", "100 BC", "1200 AD", "800 AD"], 0),
                ("Mahatma Gandhi was from?", ["India", "South Africa", "Nepal", "Pakistan"], 0)
            ]
        },
        {
            "title": "World Geography Quiz",
            "questions": [
                ("Largest continent?", ["Africa", "Asia", "Europe", "America"], 1),
                ("The Nile is in which continent?", ["Asia", "Africa", "Europe", "Australia"], 1),
                ("Mount Everest is located in?", ["China", "India", "Nepal", "Bhutan"], 2),
                ("Sahara Desert is in?", ["Africa", "Asia", "Australia", "America"], 0),
                ("Pacific Ocean is the?", ["Largest", "Smallest", "Deepest", "Shallowest"], 0)
            ]
        },
        {
            "title": "Basic Programming Quiz",
            "questions": [
                ("Python was created by?", ["Mark Zuckerberg", "Guido van Rossum", "Elon Musk", "Bill Gates"], 1),
                ("HTML stands for?", ["Hyper Trainer Marking Language", "Hyper Text Markup Language", "Hyper Text Making Language", "Hyper Text Managing Language"], 1),
                ("Which is not a programming language?", ["Python", "Java", "HTML", "C++"], 2),
                ("CSS is used for?", ["Styling", "Logic", "Database", "Networking"], 0),
                ("Which operator is used for assignment in Python?", ["=", "==", "=>", ":="], 0)
            ]
        }
    ]

    for quiz in quizzes:
        # Create quiz
        models.create_quiz(quiz["title"])
        quiz_id = models.get_all_quizzes()[-1]["id"]

        # Add questions
        for q_text, options, correct in quiz["questions"]:
            models.add_question(
                quiz_id,
                q_text,
                options[0], options[1], options[2], options[3],
                correct
            )

    print("✅ Seeding complete: 5 quizzes with 5 questions each.")


if __name__ == "__main__":
    seed_quizzes()
