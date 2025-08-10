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

    # Register API blueprints FIRST
    app.register_blueprint(quiz_service, url_prefix="/api")
    app.register_blueprint(user_service, url_prefix="/api")
    app.register_blueprint(auth_service, url_prefix="/api/auth")

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    # SPA 404 handler - this is the key fix!
    @app.errorhandler(404)
    def not_found(e):
        """
        Handle 404 errors by serving the React app's index.html for SPA routing
        This allows client-side routing to work properly on page refresh
        """
        print(f"404 handler triggered for: {e}")
        return send_from_directory(app.static_folder, 'index.html')

    # Optional: Catch-all route (you can remove this since we have the 404 handler)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        print(f"Catch-all route - Requested path: {path}")

        # API routes should never reach here due to blueprints
        if path.startswith('api/'):
            print("API path in catch-all; this shouldn't happen")
            return jsonify({"error": "API endpoint not found"}), 404

        # Try to serve static files first
        if path:
            file_path = os.path.join(app.static_folder, path)
            if os.path.isfile(file_path):
                print(f"Serving static file: {path}")
                return send_from_directory(app.static_folder, path)

        # Fallback to index.html for SPA routes
        print("Serving index.html from catch-all")
        return send_from_directory(app.static_folder, 'index.html')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)