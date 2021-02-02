"""
    PyMatcha - A Python Dating Website
    Copyright (C) 2018-2019 jlasne/gmorer
    <jlasne@student.42.fr> - <lauris.skraucis@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import datetime
import logging

from flask import Blueprint
from flask import request
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired

from uorg.models.user import User
from uorg.static import FRONTEND_PASSWORD_RESET_URL
from uorg.utils.confirm_token import confirm_token
from uorg.utils.confirm_token import generate_confirmation_token
from uorg.utils.decorators import validate_params
from uorg.utils.errors import BadRequestError
from uorg.utils.errors import NotFoundError
from uorg.utils.passwords import hash_password
from uorg.utils.success import Success
from uorg.utils.success import SuccessOutputMessage
from uorg.worker import send_mail_text

REQUIRED_KEYS_PASSWORD_FORGOT = {"email": str}
REQUIRED_KEYS_PASSWORD_RESET = {"token": str, "password": str}

password_bp = Blueprint("auth_password", __name__)


@password_bp.route("/auth/password/forgot", methods=["POST"])
@validate_params(REQUIRED_KEYS_PASSWORD_FORGOT)
def forgot_password():
    data = request.get_json()
    email = data["email"]
    if not User.get_or_none(email=email):
        logging.debug("User not found, no email sent")
        pass
    else:
        token = generate_confirmation_token(email=email, token_type="reset")
        link = FRONTEND_PASSWORD_RESET_URL + token
        logging.debug("Sending worker request to send email")
        body = """Password change request:

        Here's your password change link: {}

        Note: This link expires in an hour
        """.format(
            link
        )
        send_mail_text.delay(email, "Change your password", body)
    logging.debug("Password reset mail sent successfully for user.")
    return Success("Password reset mail sent successfully if user exists in DB.")


@password_bp.route("/auth/password/reset", methods=["POST"])
@validate_params(REQUIRED_KEYS_PASSWORD_RESET)
def reset_password():
    data = request.get_json()
    token = data["token"]
    try:
        email, token_type = confirm_token(token, expiration=7200)
    except (SignatureExpired, BadSignature) as e:
        if e == SignatureExpired:
            logging.debug(f"Signature Expired for {token}")
            raise BadRequestError("Signature Expired.", "Request another password reset and try again.")
        else:
            logging.debug(f"Bad Signature for {token}")
            raise BadRequestError("Bad Signature.", "Request another password reset and try again.")
    else:
        if token_type != "reset":
            logging.debug(f"Wrong token type for {token}")
            raise BadRequestError("Wrong token type.")
        user = User.get_or_none(email=email)
        if not user:
            raise NotFoundError("User not found.")
        user.password = hash_password(data["password"])
        user.previous_reset_token = token
        user.save()

        body = """Someone changed your password

        Hello, your password was changed on {}.
        If you believe it wasn't you, please contact us immediatly.
        """.format(
            datetime.datetime.utcnow()
        )
        send_mail_text.delay(email, "Password change notification", body)

        logging.debug("Password reset successfully")
        return Success("Password reset successful.")


@password_bp.route("/auth/password/check_token", methods=["POST"])
@validate_params({"token": str})
def check_token_validity():
    data = request.get_json()
    token = data["token"]
    try:
        email, token_type = confirm_token(token, expiration=7200)
    except (SignatureExpired, BadSignature) as e:
        if e == SignatureExpired:
            logging.debug(f"Signature Expired for {token}")
            raise BadRequestError("Signature Expired.", "Request another password reset and try again.")
        else:
            logging.debug(f"Bad Signature for {token}")
            raise BadRequestError("Bad Signature.", "Request another password reset and try again.")
    else:
        user = User.get_or_none(email=email)
        if not user:
            raise NotFoundError("User not found.")
        return SuccessOutputMessage("email", user.email, "Reset token is correct.")
