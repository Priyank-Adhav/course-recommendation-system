import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service
from routes.auth_service import auth_service

def create_app():
    static_folder_path = "/opt/render/project/src/demo-quiz-app/backend/frontend-vite/dist"
    print(f"Using hardcoded static folder path: {static_folder_path}")

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

    app.register_blueprint(quiz_service, url_prefix="/api")
    app.register_blueprint(user_service, url_prefix="/api")
    app.register_blueprint(auth_service, url_prefix="/api/auth")

    @app.route('/')
    def index():
        print("Serving / -> index.html")
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_frontend(path):
        print(f"Requested path: {path}")
        if path.startswith('api/') or path.startswith('auth/'):
            print("API or Auth path detected; returning 404")
            return "Not Found", 404

        file_path = os.path.join(app.static_folder, path)
        print(f"Checking file path: {file_path}")
        if os.path.exists(file_path):
            print(f"Serving file: {path}")
            return send_from_directory(app.static_folder, path)

        print("Serving fallback index.html")
        return send_from_directory(app.static_folder, 'index.html')

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
