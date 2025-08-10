import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service
from routes.auth_service import auth_service

def create_app():
    # Fix: Use absolute path for static folder
    static_folder_path = os.path.join(os.path.dirname(__file__), 'frontend-vite', 'dist')
    print(f"Static folder path: {static_folder_path}") # Debug print
    
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

    # Auto-seed the database on startup
    try:
        import seed_data
        print("🌱 Running seed data...")
        seed_data.seed_data()
        print("✅ Seed data completed")
    except Exception as e:
        print(f"⚠️  Seed data failed (this is normal if data already exists): {e}")

    # Register blueprints
    app.register_blueprint(quiz_service, url_prefix="/api")
    app.register_blueprint(user_service, url_prefix="/api")
    app.register_blueprint(auth_service, url_prefix="/api/auth")

    # Serve frontend for all non-API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Let Flask handle API/auth routes
        if path.startswith('api/') or path.startswith('auth/'):
            return "Not Found", 404 # Allows blueprints to catch it

        # Try to serve static file
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)

        # Fallback to index.html for SPA routing
        return send_from_directory(app.static_folder, 'index.html')

    # Health check
    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))