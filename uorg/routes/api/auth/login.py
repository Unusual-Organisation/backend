from datetime import datetime

from flask import Blueprint
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jti
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_refresh_token_required

from uorg import redis
from uorg.models.user import User
from uorg.static import ACCESS_TOKEN_EXPIRES
from uorg.static import REFRESH_TOKEN_EXPIRES
from uorg.utils.decorators import validate_params
from uorg.utils.errors import UnauthorizedError
from uorg.utils.passwords import check_password
from uorg.utils.success import Success
from uorg.utils.success import SuccessOutput
from uorg.worker import send_mail_text


login_bp = Blueprint("login", __name__)

REQUIRED_KEYS_LOGIN = {"email": str, "password": str}


@login_bp.route("/auth/login", methods=["POST"])
@validate_params(REQUIRED_KEYS_LOGIN)
def login_user():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    try:
        user = User.get(email=email)
    except User.DoesNotExist:
        raise UnauthorizedError("Incorrect username or password.")
    if not check_password(user.password, password):
        raise UnauthorizedError("Incorrect username or password.")

    if not user.is_confirmed:
        raise UnauthorizedError("User needs to be confirmed first.", "Try again when you have confirmed your email.")

    access_token = create_access_token(identity=user.get_jwt_info(), fresh=True)
    refresh_token = create_refresh_token(identity=user.get_jwt_info())
    access_jti = get_jti(access_token)
    refresh_jti = get_jti(refresh_token)

    redis.set("is_revoked_jti:" + access_jti, "false", ACCESS_TOKEN_EXPIRES * 1.2)
    redis.set("is_revoked_jti:" + refresh_jti, "false", REFRESH_TOKEN_EXPIRES * 1.2)
    ret = {"access_token": access_token, "refresh_token": refresh_token, "user_id": user.id}

    send_mail_text.delay(
        dest=user.email,
        subject="[Unusual Organisation] Login notification",
        body=f"Someone logged in into your account at {datetime.utcnow()}."
        f"If you believe it wasn't you, please change your password immediately!",
    )
    return SuccessOutput("return", ret)


@login_bp.route("/auth/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    access_jti = get_jti(encoded_token=access_token)
    redis.set("is_revoked_jti:" + access_jti, "false", ACCESS_TOKEN_EXPIRES * 1.2)
    return SuccessOutput("access_token", access_token)


@login_bp.route("/auth/logout", methods=["POST"])
@validate_params({"access_token": str, "refresh_token": str})
def logout():
    data = request.get_json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    access_jti = get_jti(access_token)
    refresh_jti = get_jti(refresh_token)
    redis.set("is_revoked_jti:" + access_jti, "true", ACCESS_TOKEN_EXPIRES * 1.2)
    redis.set("is_revoked_jti:" + refresh_jti, "true", REFRESH_TOKEN_EXPIRES * 1.2)
    return Success("Logout successful.")
