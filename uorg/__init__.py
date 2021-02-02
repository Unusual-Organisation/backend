import logging
import os

import peewee
from celery import Celery
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from redis import StrictRedis

from uorg.utils.logging import setup_logging


ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(ROOT, ".env")
load_dotenv(dotenv_path)

REQUIRED_ENV_VARS = [
    "FLASK_PORT",
    "FLASK_DEBUG",
    "FLASK_HOST",
    "FLASK_SECRET_KEY",
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "MAIL_SERVER",
    "MAIL_PORT",
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "MAIL_DEFAULT_SENDER",
    "FRONTEND_URL",
]

for item in REQUIRED_ENV_VARS:
    if item not in os.environ:
        raise EnvironmentError(f"{item} is not set in the server's environment or .env file. It is required.")

from uorg.static import (
    FLASK_SECRET_KEY,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
    DB_HOST,
    REDIS_PORT,
    REDIS_HOST,
    ACCESS_TOKEN_EXPIRES,
    REFRESH_TOKEN_EXPIRES,
    CELERY_RESULT_BACKEND,
    CELERY_BROKER_URL,
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER,
)

setup_logging()

application = Flask(__name__)

if os.getenv("FLASK_DEBUG", "false") == "true" or os.getenv("FLASK_DEBUG", "false") == "1":
    application.debug = True
else:
    application.debug = False

application.secret_key = FLASK_SECRET_KEY
application.config.update(FLASK_SECRET_KEY=FLASK_SECRET_KEY)
application.config["JWT_SECRET_KEY"] = FLASK_SECRET_KEY
application.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
logging.debug("Configuring Celery Redis URLs")
application.config["CELERY_broker_url"] = CELERY_BROKER_URL
application.config["result_backend"] = CELERY_RESULT_BACKEND

logging.debug("Initializing Celery")
# Initialize Celery
celery = Celery(application.name, broker=CELERY_BROKER_URL)
celery.conf.update(application.config)


logging.debug("Configuring mail settings")
application.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_DEBUG=False,
    MAIL_DEFAULT_SENDER=MAIL_DEFAULT_SENDER,
)
logging.debug("Configuring mail")
mail = Mail(application)


logging.debug("Configuring JWT")

application.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_TOKEN_EXPIRES
application.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_TOKEN_EXPIRES
application.config["JWT_BLACKLIST_ENABLED"] = True
application.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

jwt = JWTManager(application)


logging.debug("Configuring CORS")
CORS(application, expose_headers="Authorization", supports_credentials=True)

logging.debug("Connecting to database")

logging.debug("Connecting to redis")
redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, db=2)


# Initializes the PostgreSQL DB
uorg_db = peewee.MySQLDatabase(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

import uorg.utils.jwt_callbacks  # noqa

from uorg.routes.api.home import home_bp
from uorg.routes.api.auth.register import register_bp
from uorg.routes.api.auth.login import login_bp
from uorg.routes.api.auth.password import password_bp

logging.debug("Registering Flask blueprints")
application.register_blueprint(home_bp)
application.register_blueprint(register_bp)
application.register_blueprint(login_bp)
application.register_blueprint(password_bp)

# import tasks here to be registered by celery

from uorg.worker import *  # noqa

from uorg.models.user import User

if not User.table_exists():
    User.create_table()
