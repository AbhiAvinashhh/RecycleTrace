"""
RecycleTrace - Application Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/recycletrace_db")
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), os.environ.get("UPLOAD_FOLDER", "uploads"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "10")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "mp4", "avi", "csv", "xlsx"}

    # Session / Cookie
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = 3600 * 8  # 8 hours

    # Weight tolerance
    WEIGHT_TOLERANCE_PERCENT = float(os.environ.get("WEIGHT_TOLERANCE_PERCENT", "5"))

    # Rate limiting (simple in-memory for dev)
    LOGIN_RATE_LIMIT = int(os.environ.get("LOGIN_RATE_LIMIT", "10"))

    # CSRF protection (WTForms / Flask-WTF)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False   # easier during API testing in dev


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.environ.get("TEST_MONGO_URI", "mongodb://localhost:27017/recycletrace_test")
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": Config,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, config_map["default"])
