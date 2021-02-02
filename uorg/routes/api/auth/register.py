import logging
from datetime import datetime

from flask import Blueprint
from flask import request
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired

from uorg.models.user import User
from uorg.static import FRONTEND_EMAIL_CONFIRMATION_URL
from uorg.utils.confirm_token import confirm_token
from uorg.utils.confirm_token import generate_confirmation_token
from uorg.utils.decorators import validate_params
from uorg.utils.errors import BadRequestError
from uorg.utils.errors import NotFoundError
from uorg.utils.success import Success
from uorg.worker import send_mail_text

register_bp = Blueprint("register", __name__)

REQUIRED_KEYS_USER_REGISTER = {"first_name": str, "last_name": str, "email": str, "password": str}
REQUIRED_KEYS_NEW_EMAIL_CONF = {"email": str}


@register_bp.route("/auth/register", methods=["POST"])
@validate_params(REQUIRED_KEYS_USER_REGISTER)
def register_user():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    password = data["password"]

    User.register(first_name=first_name, last_name=last_name, email=email, password=password)
    token = generate_confirmation_token(email=email, token_type="confirm")
    link = FRONTEND_EMAIL_CONFIRMATION_URL + token
    body = """Thank you for creating an account on Unusual Organisation!

    Here's your confirmation link: {}

    Note: This link expires in an hour
    """.format(
        link
    )
    send_mail_text.delay(email, "Confirm your account", body)
    return Success("User created successfully.")


@register_bp.route("/auth/confirm/<token>", methods=["POST"])
def confirm_email(token):
    try:
        email, token_type = confirm_token(token, expiration=7200)
    except (SignatureExpired, BadSignature) as e:
        if e == SignatureExpired:
            logging.debug(f"Signature Expired for token {token}")
            raise BadRequestError("Signature Expired.", "Request another email confirmation and try again.")
        else:
            logging.debug(f"Bad Expired for token {token}")
            raise BadRequestError("Bad Signature.", "Request another password reset and try again.")
    else:
        if token_type != "confirm":
            logging.debug(f"Wrong token type for token {token}")
            raise BadRequestError("Wrong token type.")

        user = User.get_or_none(email=email)
        if not user:
            raise NotFoundError("User not found.")
        if user.is_confirmed:
            logging.debug("User already confirmed")
            raise BadRequestError("Email already confirmed.", "")
        else:
            user.is_confirmed = True
            user.confirmed_on = datetime.utcnow()
            user.save()
        logging.debug(f"User {user.id} confirmed.")
        return Success("Confirmation successful.")


@register_bp.route("/auth/confirm/new", methods=["POST"])
@validate_params(REQUIRED_KEYS_NEW_EMAIL_CONF)
def request_new_email_conf():
    data = request.get_json()
    email = data["email"]
    user = User.get_or_none(email=email)
    if not user:
        pass
    else:
        if user.is_confirmed:
            logging.debug("Already confirmed.")
        else:
            logging.debug("/auth/confirm/new -> User found, sending new confirmation email")
            token = generate_confirmation_token(email=email, token_type="confirm")
            link = FRONTEND_EMAIL_CONFIRMATION_URL + token
            body = """Thank you for creating an account on Unusual Organisation!

            Here's your confirmation link: {}

            Note: This link expires in an hour
            """.format(
                link
            )
            send_mail_text.delay(email, "Confirm your account", body)
    logging.debug("/auth/confirm/new -> New confirmation email sent if user exists in database")
    return Success("New confirmation email sent if user exists in database and isn't already confirmed.")
