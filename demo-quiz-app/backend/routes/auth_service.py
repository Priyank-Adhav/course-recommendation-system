from flask import Blueprint, request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from models import models

auth_service = Blueprint("auth_service", __name__)

def _ser():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth-token")

def _make_token(user_id):
    return _ser().dumps({"uid": int(user_id)})

def _verify_token(token, max_age=60*60*24*7):
    data = _ser().loads(token, max_age=max_age)
    return int(data["uid"])

@auth_service.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not name or not email or not password:
        return jsonify({"error": "name, email, password required"}), 400
    if models.get_user_by_email(email):
        return jsonify({"error": "User already exists"}), 400
    models.create_user_secure(name, email, password)
    user = models.get_user_by_email(email)
    token = _make_token(user["id"])
    return jsonify({"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}), 201

@auth_service.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = models.verify_user_credentials(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = _make_token(user["id"])
    return jsonify({"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})

@auth_service.route("/me", methods=["GET"])
def me():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    try:
        uid = _verify_token(auth.split(" ", 1)[1])
        user = models.get_user_by_id(uid)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"id": user["id"], "name": user["name"], "email": user["email"]})
    except (BadSignature, SignatureExpired):
        return jsonify({"error": "Invalid token"}), 401