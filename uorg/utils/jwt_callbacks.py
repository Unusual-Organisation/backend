import logging

from flask import jsonify

from uorg import jwt
from uorg import redis
from uorg.models.user import User


logging.debug("Configuring JWT callbacks")


@jwt.expired_token_loader
def expired_token_callback(expired_token):
    resp = {
        "message": f"The {expired_token['type']} token has expired",
        "name": "Unauthorized Error",
        "solution": "Try again when you have renewed your token",
        "type": "UnauthorizedError",
    }
    return jsonify(resp), 401


@jwt.user_loader_callback_loader
def jwt_user_callback(identity):
    return User.get_or_none(id=identity["id"])


@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token["jti"]
    entry = redis.get("is_revoked_jti:" + jti)
    if entry is None:
        return True
    return entry == "true"


@jwt.revoked_token_loader
def jwt_revoked_token_callback():
    return (
        jsonify(
            {
                "message": "Token has been revoked.",
                "name": "Unauthorized Error",
                "solution": "Please login again",
                "type": "UnauthorizedError",
            }
        ),
        401,
    )


@jwt.unauthorized_loader
def no_jwt_callback(error_message):
    return (
        jsonify(
            {
                "message": error_message,
                "name": "Unauthorized Error",
                "solution": "Try again",
                "type": "UnauthorizedError",
            }
        ),
        401,
    )


@jwt.invalid_token_loader
def jwt_invalid_token_callback(error_message):
    return (
        jsonify(
            {
                "message": error_message,
                "name": "Bad Request Error",
                "solution": "Try again (The token is invalid)",
                "type": "BadRequestError",
            }
        ),
        400,
    )
