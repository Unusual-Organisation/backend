from uorg import application
from uorg.utils.errors.base_class import CustomException
from uorg.utils.errors.template import generate_error_json


class UnauthorizedError(CustomException):
    """
    This is the UnauthorizedError class for the Exception.
    """

    def __init__(self, msg: str, solution: str = "Try again.") -> None:
        self.name = "Unauthorized Error"
        self.msg = msg
        self.solution = solution
        self.status_code = 401

    pass


@application.errorhandler(UnauthorizedError)  # type: ignore
def generate_unauthorized(error: UnauthorizedError) -> dict:
    """
    This is the 401 response creator. It will create a 401 response with
    a custom message and the 401 code.

    :param error: The error body
    :return: Returns the response formatted
    """

    return generate_error_json(error, 401)
