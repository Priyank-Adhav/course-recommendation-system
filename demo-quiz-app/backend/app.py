from flask import Flask
from flask_cors import CORS
import os

# Import routes (will add actual logic later)
from routes.quiz_service import quiz_bp
from routes.user_service import user_bp

def create_app():
    app = Flask(__name__)

    # Load config
    app.config.from_object("config.Config")

    # Enable CORS (so React can call the API)
    CORS(app)

    # Register blueprints
    app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
    app.register_blueprint(user_bp, url_prefix="/api/user")

    # Health check route
    @app.route("/ping", methods=["GET"])
    def ping():
        return {"status": "ok", "message": "Server is running!"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
