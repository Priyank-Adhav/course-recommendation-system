from flask import Blueprint

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/test", methods=["GET"])
def test_quiz():
    return {"message": "Quiz service is working"}, 200
