from uorg import application
from uorg.utils.errors.base_class import CustomException
from uorg.utils.errors.template import generate_error_json


class NotFoundError(CustomException):
    """
    This is the NotFoundError class for the Exception.
    """

    def __init__(self, msg: str, solution: str = "Try again.") -> None:
        self.name = "Not Found Error"
        self.msg = msg
        self.solution = solution
        self.status_code = 404

    pass


@application.errorhandler(NotFoundError)  # type: ignore
def generate_notfound(error: NotFoundError) -> dict:
    """
    This is the 404 response creator. It will create a 404 response with
    a custom message and the 404 code.

    :param error: The error body
    :return: Returns the response formatted
    """

    return generate_error_json(error, 404)
