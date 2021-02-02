from uorg import application
from uorg.utils.errors.base_class import CustomException
from uorg.utils.errors.template import generate_error_json


class ForbiddenError(CustomException):
    """
    This is the ForbiddenError class for the Exception.
    """

    def __init__(self, msg: str, solution: str = "Try again.") -> None:
        self.name = "Forbidden Error"
        self.msg = msg
        self.solution = solution
        self.status_code = 403

    pass


@application.errorhandler(ForbiddenError)
def generate_forbidden(error: ForbiddenError) -> dict:
    """
    This is the 403 response creator. It will create a 403 response along with
    a custom message and the 403 code

    :param error: The error body
    :return: Returns the response formatted
    """

    return generate_error_json(error, 403)
