import datetime
import os

FLASK_PORT = os.getenv("FLASK_PORT")
FLASK_DEBUG = os.getenv("FLASK_DEBUG")
FLASK_HOST = os.getenv("FLASK_HOST")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

ROOT_PATH = os.path.join(os.path.dirname(__file__), "../")

FRONTEND_URL = os.getenv("FRONTEND_URL")

ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)

FRONTEND_EMAIL_CONFIRMATION_URL = FRONTEND_URL + "/register/confirm/"
FRONTEND_PASSWORD_RESET_URL = FRONTEND_URL + "/password/reset/"
