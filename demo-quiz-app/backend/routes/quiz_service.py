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

@quiz_service.route("/submit_answers", methods=["POST"])
def submit_answers():
    data = request.json or {}

    # Validate quiz_id
    try:
        quiz_id = int(data.get("quiz_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "quiz_id must be an integer"}), 400

    # Validate answers
    answers = data.get("answers")
    if not isinstance(answers, dict) or not answers:
        return jsonify({"error": "answers must be a non-empty object"}), 400

    # Get correct answers and guard None
    correct_answers = models.get_correct_answers(quiz_id) or {}  # e.g. {question_id: "1"}
    # Normalize to ints
    try:
        correct_answers = {int(qid): int(opt) for qid, opt in correct_answers.items()}
    except Exception:
        return jsonify({"error": "malformed correct answers in DB"}), 500

    score = 0
    total = 0
    for qid_str, user_ans in answers.items():
        try:
            qid = int(qid_str)
            user_opt = int(user_ans)
        except (TypeError, ValueError):
            continue
        total += 1
        if correct_answers.get(qid) == user_opt:
            score += 1

    return jsonify({"score": score, "total": total}), 200