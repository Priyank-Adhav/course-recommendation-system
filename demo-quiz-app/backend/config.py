import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_FILE = os.path.join(BASE_DIR, "quiz_app.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
