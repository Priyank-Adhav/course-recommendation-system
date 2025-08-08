from flask import Flask
from flask_cors import CORS
from routes.quiz_service import quiz_service
from routes.user_service import user_service

app = Flask(__name__)
CORS(app)  # allow frontend to call backend from another port (e.g., React on 3000)

# Register blueprints
app.register_blueprint(quiz_service, url_prefix="/quiz")
app.register_blueprint(user_service, url_prefix="/user")

if __name__ == "__main__":
    app.run(debug=True)
