from flask import Blueprint, request, jsonify
from models import models # your models file from above

quiz_service = Blueprint("quiz_service", __name__)

# ---------------- USERS ----------------
@quiz_service.route("/users", methods=["POST"])
def create_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    models.create_user(name, email)
    return jsonify({"message": "User created successfully"}), 201


# ---------------- CATEGORIES ----------------
@quiz_service.route("/categories", methods=["POST"])
def create_category():
    data = request.json
    unique_id = data.get("unique_id")
    name = data.get("name")

    if not unique_id or not name:
        return jsonify({"error": "unique_id and name are required"}), 400

    models.create_category(unique_id, name)
    return jsonify({"message": "Category created successfully"}), 201


@quiz_service.route("/categories", methods=["GET"])
def list_categories():
    categories = models.get_all_categories()
    return jsonify([dict(c) for c in categories])


# ---------------- QUIZZES ----------------
@quiz_service.route("/quizzes", methods=["POST"])
def create_quiz():
    data = request.json
    title = data.get("title")
    category_id = data.get("category_id")

    if not title or not category_id:
        return jsonify({"error": "title and category_id are required"}), 400

    models.create_quiz(title, category_id)
    return jsonify({"message": "Quiz created successfully"}), 201


@quiz_service.route("/quizzes", methods=["GET"])
def list_quizzes():
    quizzes = models.get_all_quizzes()
    return jsonify([dict(q) for q in quizzes])


# ---------------- QUESTIONS ----------------
@quiz_service.route("/questions", methods=["POST"])
def add_question():
    data = request.json

    if isinstance(data, list):
        for q in data:
            _add_question_internal(q)
    else:
        _add_question_internal(data)

    return jsonify({"message": "Question(s) added successfully"}), 201


def _add_question_internal(q):
    quiz_id = q.get("quiz_id")
    question_text = q.get("question_text")
    options = q.get("options", [])
    correct_option = q.get("correct_option")
    teacher_id = q.get("teacher_id")
    label_id = q.get("label_id")
    unique_id = q.get("unique_id")

    if not quiz_id or not question_text or not options or correct_option is None:
        raise ValueError("quiz_id, question_text, options, and correct_option are required")

    models.add_question(
        quiz_id,
        question_text,
        options[0] if len(options) > 0 else None,
        options[1] if len(options) > 1 else None,
        options[2] if len(options) > 2 else None,
        options[3] if len(options) > 3 else None,
        correct_option,
        teacher_id,
        label_id,
        unique_id
    )


@quiz_service.route("/questions/<int:quiz_id>", methods=["GET"])
def get_questions(quiz_id):
    questions = models.get_questions_for_quiz(quiz_id)
    return jsonify([dict(q) for q in questions])


# ---------------- SUBMIT ANSWERS ----------------
@quiz_service.route("/submit", methods=["POST"])
def submit_answers():
    data = request.json or {}

    try:
        quiz_id = int(data.get("quiz_id"))
        user_id = int(data.get("user_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "quiz_id and user_id must be integers"}), 400

    answers = data.get("answers")  # {question_id: selected_option}
    times = data.get("times", {})  # optional {question_id: time_taken}

    if not isinstance(answers, dict) or not answers:
        return jsonify({"error": "answers must be a non-empty object"}), 400

    correct_answers = models.get_correct_answers(quiz_id) or {}
    score = 0
    total = len(answers)

    for qid, user_ans in answers.items():
        try:
            qid_int = int(qid)
            if correct_answers.get(qid_int) == int(user_ans):
                score += 1
        except (ValueError, TypeError):
            pass

    result_id = models.save_result(
        user_id=user_id,
        quiz_id=quiz_id,
        total_questions=total,
        correct_questions=score,
        time_taken=data.get("time_taken", 0),
        score=score
    )

    for qid, user_ans in answers.items():
        correct_opt = correct_answers.get(int(qid))
        models.save_result_per_question(
            result_id=result_id,
            question_id=int(qid),
            points=1 if correct_opt == int(user_ans) else 0,
            correct_ans=correct_opt,
            submitted_ans=user_ans,
            time_taken=times.get(str(qid), 0)
        )

    return jsonify({"result_id": result_id, "score": score, "total": total}), 200


# ---------------- RESULTS ----------------
@quiz_service.route("/results/<int:user_id>", methods=["GET"])
def get_user_results(user_id):
    results = models.get_results_for_user(user_id)
    return jsonify([dict(r) for r in results])


@quiz_service.route("/result_details/<int:result_id>", methods=["GET"])
def get_result_details(result_id):
    details = models.get_result_details(result_id)
    return jsonify([dict(d) for d in details])


# ---------------- UTILITIES ----------------
@quiz_service.route("/clear_all", methods=["POST"])
def clear_all_data():
    models.clear_all_data()
    return jsonify({"message": "All data cleared"}), 200
