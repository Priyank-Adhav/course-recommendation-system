from flask import Blueprint, request, jsonify
from models import models

quiz_service = Blueprint("quiz_service", __name__)

# ---------------- CREATE QUIZ ----------------
@quiz_service.route("/create", methods=["POST"])
def create_quiz():
    data = request.json
    title = data.get("title")

    if not title:
        return jsonify({"error": "Quiz title is required"}), 400

    models.create_quiz(title)
    return jsonify({"message": "Quiz created successfully"}), 201


# ---------------- LIST QUIZZES ----------------
@quiz_service.route("/list", methods=["GET"])
def list_quizzes():
    quizzes = models.get_all_quizzes()
    quizzes_list = [dict(q) for q in quizzes]
    return jsonify(quizzes_list)


@quiz_service.route("/add_question", methods=["POST"])
def add_question():
    data = request.json

    if isinstance(data, list):  # multiple questions
        for q in data:
            quiz_id = q.get("quiz_id")
            question_text = q.get("question_text")
            options = q.get("options", [])
            correct = q.get("correct_option")

            if not quiz_id or not question_text or not options or correct is None:
                return jsonify({"error": "quiz_id, question_text, options, and correct_option are required"}), 400

            models.add_question(
                quiz_id,
                question_text,
                options[0] if len(options) > 0 else None,
                options[1] if len(options) > 1 else None,
                options[2] if len(options) > 2 else None,
                options[3] if len(options) > 3 else None,
                correct
            )
    else:  # single question
        quiz_id = data.get("quiz_id")
        question_text = data.get("question_text")
        options = data.get("options", [])
        correct = data.get("correct_option")

        if not quiz_id or not question_text or not options or correct is None:
            return jsonify({"error": "quiz_id, question_text, options, and correct_option are required"}), 400

        models.add_question(
            quiz_id,
            question_text,
            options[0] if len(options) > 0 else None,
            options[1] if len(options) > 1 else None,
            options[2] if len(options) > 2 else None,
            options[3] if len(options) > 3 else None,
            correct
        )

    return jsonify({"message": "Question(s) added successfully"}), 201


# ---------------- GET QUESTIONS FOR QUIZ ----------------
@quiz_service.route("/questions/<int:quiz_id>", methods=["GET"])
def get_questions(quiz_id):
    questions = models.get_questions_for_quiz(quiz_id)
    questions_list = [dict(q) for q in questions]
    return jsonify(questions_list)
