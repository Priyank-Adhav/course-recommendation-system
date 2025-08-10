import os
from flask import Flask
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service
from routes.auth_service import auth_service

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    CORS(app)  # or CORS(app, resources={r"/*": {"origins": os.environ.get("CORS_ORIGIN", "*")}})
    import database
    database.init_db()
    try:
        database.ensure_password_column()
    except Exception:
        pass
    app.register_blueprint(quiz_service)
    app.register_blueprint(user_service)
    app.register_blueprint(auth_service, url_prefix="/auth")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))