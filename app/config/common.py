import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

#Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "YOUR-FALLBACK-SECRET-KEY")

# Database
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# RateLimit
RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "False") == "True"
RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

# redis
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_URL = f'redis://:@localhost:{REDIS_PORT}/0'


class Config:
    # Flask
    TESTING = True
    DEBUG = True
    SECRET_KEY = SECRET_KEY
    # Database
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    # Ratelimit
    RATELIMIT_ENABLED = RATELIMIT_ENABLED
    RATELIMIT_STORAGE_URI = RATELIMIT_STORAGE_URI
    RATELIMIT_STRATEGY = "fixed-window"  # or "moving-window"
    RATELIMIT_IN_MEMORY_FALLBACK_ENABLED = True
    RATELIMIT_HEADERS_ENABLED = True
    # Redis
    REDIS_URL = REDIS_URL
    # Misc
    DATETIME_STRING_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


if __name__ == '__main__':
    # test
    print(f'DATABSE: {Config.SQLALCHEMY_DATABASE_URI}')