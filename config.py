import os
import secrets
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER = os.environ.get('DB_USER', '')
    DB_PASSWORD = quote_plus(os.environ.get('DB_PASSWORD', ''))
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', '')

    ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Fail-fast in production if DB_NAME is missing
    if ENV == 'production' and not DB_NAME:
        raise RuntimeError("Database configuration (DB_NAME) is required in production.")
        
    if DB_NAME:
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 280,
            "pool_timeout": 20,
            "pool_size": 5,
            "max_overflow": 2,
        }
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///local.db'
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Fix: Prevent hardcoded fallback in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if ENV == 'production':
            raise RuntimeError("SECRET_KEY environment variable must be set in production.")
        SECRET_KEY = secrets.token_hex(32)