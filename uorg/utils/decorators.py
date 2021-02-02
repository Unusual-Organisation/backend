from functools import wraps
from typing import Optional

from flask import request
from werkzeug.exceptions import BadRequest

from uorg.utils.errors import BadRequestError


def validate_params(required: dict, optional: Optional[dict] = None, allow_empty=False):
    if optional is None:
        optional = {}

    def decorator(fn):
        """Decorator that checks for the required parameters"""

        @wraps(fn)
        def wrapper(*args, **kwargs):
            # If the json body is missing something (`,` for example), throw an error
            try:
                data = request.get_json()
            except BadRequest:
                raise BadRequestError("The Json Body is malformed.")

            # If the data dict is empty
            if not data:
                raise BadRequestError("Missing json body.")

            if not isinstance(data, dict):
                raise BadRequestError("JSON body must be a dict")

            missing = []
            for item in required.keys():
                # If a key is missing in the sent data
                if item not in data.keys():
                    missing.append(item)
            if missing:
                raise BadRequestError("Missing keys {}.".format(missing), "Complete your json body and try again.")

            for item in data.keys():
                # If there's an unwanted key in the sent data
                if item not in required.keys() and item not in optional.keys():
                    raise BadRequestError(
                        "You can't specify key '{}'.".format(item),
                        "You are only allowed to specify the fields {}" ".".format(required.keys()),
                    )

            if not allow_empty:
                for key, value in data.items():
                    if not value:
                        if required[key] == int or required[key] == bool:
                            pass
                        else:
                            raise BadRequestError(f"The item {key} cannot be None or empty.")

            wrong_types = [r for r in required.keys() if not isinstance(data[r], required[r])]
            wrong_types += [r for r in optional.keys() if r in data and not isinstance(data[r], optional[r])]

            if wrong_types:
                raise BadRequestError(
                    "{} is/are the wrong type.".format(wrong_types),
                    "It/They must be respectively {} and {}".format(required, optional),
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
