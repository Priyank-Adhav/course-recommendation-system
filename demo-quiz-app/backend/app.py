import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service
from routes.auth_service import auth_service

def create_app():
    # Hardcode the absolute path to frontend build folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_folder_path = os.path.join(BASE_DIR, 'frontend-vite', 'dist')
    print(f"Using static folder: {static_folder_path}")

    app = Flask(
        __name__,
        static_folder=static_folder_path,
        static_url_path=''
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    CORS(app)

    import database
    database.init_db()
    try:
        database.ensure_password_column()
    except Exception:
        pass

    # Register blueprints
    app.register_blueprint(quiz_service, url_prefix="/api")
    app.register_blueprint(user_service, url_prefix="/api")
    app.register_blueprint(auth_service, url_prefix="/api/auth")

    # Explicit root route
    @app.route('/')
    def index():
        return send_from_directory(static_folder_path, 'index.html')

    # Catch-all route for SPA paths, except API/Auth
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api/') or path.startswith('auth/'):
            return "Not Found", 404

        full_path = os.path.join(static_folder_path, path)
        if os.path.exists(full_path):
            return send_from_directory(static_folder_path, path)
        else:
            return send_from_directory(static_folder_path, 'index.html')

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
