import os
from flask import Flask
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service
from routes.auth_service import auth_service
import database

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    CORS(app)  # Enable CORS for all routes
    
    # Initialize database
    database.init_db()
    database.ensure_password_column()  
    
    # Register blueprint
    app.register_blueprint(quiz_service)
    app.register_blueprint(user_service)
    app.register_blueprint(auth_service, url_prefix="/auth") 
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Flask Quiz Application...")
    print("📍 Server running at: http://localhost:5000")
    print("🔗 Available endpoints:")
    print("   POST /users - Create user")
    print("   POST /categories - Create category") 
    print("   GET  /categories - List categories")
    print("   POST /quizzes - Create quiz")
    print("   GET  /quizzes - List quizzes")
    print("   POST /questions - Add questions")
    print("   GET  /questions/<quiz_id> - Get questions")
    print("   POST /submit - Submit quiz answers")
    print("   GET  /results/<user_id> - Get user results")
    print("   GET  /result_details/<result_id> - Get result details")
    print("   POST /clear_all - Clear all data")
    print("\n💡 Run 'python seed_data.py' in another terminal to populate with test data")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)