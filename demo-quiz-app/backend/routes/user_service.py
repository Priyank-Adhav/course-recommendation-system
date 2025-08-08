from flask import Blueprint

user_bp = Blueprint("user", __name__)

@user_bp.route("/test", methods=["GET"])
def test_user():
    return {"message": "User service is working"}, 200
