import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service
from routes.auth_service import auth_service

def create_app():
    app = Flask(__name__, 
                static_folder='../frontend-vite/dist',
                static_url_path='')
    
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
    
    # Serve frontend for all non-API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api/') or path.startswith('auth/'):
            # Let API routes handle these
            return app.send_static_file('index.html')
        
        # Try to serve the file, fallback to index.html for SPA routing
        try:
            return send_from_directory(app.static_folder, path)
        except:
            return send_from_directory(app.static_folder, 'index.html')
    
    # Health check
    @app.get("/health")
    def health():
        return jsonify({"ok": True})
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))