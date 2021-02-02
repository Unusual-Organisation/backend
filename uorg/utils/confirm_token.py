import logging

from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import URLSafeTimedSerializer

from uorg import application

ACCEPTED_TOKEN_TYPES = ["confirm", "reset"]


def generate_confirmation_token(email, token_type):
    logging.debug("Generating confirmation token for email {}".format(email))
    if token_type not in ACCEPTED_TOKEN_TYPES:
        logging.warning("token_type must be of {} and is {}".format(ACCEPTED_TOKEN_TYPES, token_type))
        raise ValueError("Reset token type must be confirm or reset.")
    serializer = URLSafeTimedSerializer(application.config["FLASK_SECRET_KEY"])
    token = serializer.dumps(email + ":{}".format(token_type), salt=application.config["FLASK_SECRET_KEY"])
    logging.debug("Generated token {} for email {}".format(token, email))
    return token


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(application.config["FLASK_SECRET_KEY"])
    try:
        logging.debug("Trying to confirm token {}")
        ret = serializer.loads(token, salt=application.config["FLASK_SECRET_KEY"], max_age=expiration)
        email = ret.split(":")[0]
        token_type = ret.split(":")[1]
    except (SignatureExpired, BadSignature) as e:
        raise e
    logging.debug("Confirmed token {} for email {} of type {}".format(token, email, token_type))
    return email, token_type
