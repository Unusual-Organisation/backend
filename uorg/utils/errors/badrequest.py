from uorg import application
from uorg.utils.errors.base_class import CustomException
from uorg.utils.errors.template import generate_error_json


class BadRequestError(CustomException):
    """
    This is the BadRequestError class for the Exception.
    """

    def __init__(self, msg: str, solution: str = "Try again.") -> None:
        self.name = "Bad Request"
        self.msg = msg
        self.solution = solution
        self.status_code = 400

    pass


@application.errorhandler(BadRequestError)  # type: ignore
def generate_badrequest(error: BadRequestError) -> dict:
    """
    This is the 400 response creator. It will create a 400 response along with
    a custom message and the 400 code

    :param error: The error body
    :return: Returns the response formatted
    """
    return generate_error_json(error, 400)
