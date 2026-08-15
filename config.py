import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_USER = os.environ.get('DB_USER', '')
    DB_PASSWORD = quote_plus(os.environ.get('DB_PASSWORD', ''))
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', '')

    # اگر نام دیتابیس در .env تنظیم شده باشد از MySQL استفاده می‌کند،
    # در غیر این صورت روی سیستم شخصی از SQLite استفاده خواهد شد.
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
        # دیتابیس سبک و بدون نیاز به نصب برای کامپیوتر شخصی
        SQLALCHEMY_DATABASE_URI = 'sqlite:///local.db'
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'in yek kelid amniyati ast hahaha')