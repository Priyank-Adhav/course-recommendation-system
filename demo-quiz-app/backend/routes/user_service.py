from flask import Blueprint, request, jsonify
from models import models

user_service = Blueprint("user_service", __name__)

# ---------------- REGISTER USER ----------------
@user_service.route("/register", methods=["POST"])
def register_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    if models.get_user_by_email(email):
        return jsonify({"error": "User already exists"}), 400

    models.create_user(name, email)
    return jsonify({"message": "User registered successfully"}), 201


# ---------------- GET USER SCORES ----------------
@user_service.route("/scores/<email>", methods=["GET"])
def get_scores(email):
    user = models.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    scores = models.get_scores_for_user(user["id"])
    scores_list = [dict(s) for s in scores]
    return jsonify(scores_list)


# ---------------- SAVE SCORE ----------------
@user_service.route("/save_score", methods=["POST"])
def save_score():
    data = request.json
    email = data.get("email")
    quiz_id = data.get("quiz_id")
    score = data.get("score")

    if not email or quiz_id is None or score is None:
        return jsonify({"error": "email, quiz_id, and score are required"}), 400

    user = models.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    models.save_score(user["id"], quiz_id, score)
    return jsonify({"message": "Score saved successfully"}), 201
