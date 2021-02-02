from uorg import application
from uorg.utils.errors.base_class import CustomException
from uorg.utils.errors.template import generate_error_json


class ConflictError(CustomException):
    """
    This is the ConflictError class for the Exception.
    """

    def __init__(self, msg: str, solution: str = "Try again.") -> None:
        self.name = "Conflict Error"
        self.msg = msg
        self.solution = solution
        self.status_code = 409

    pass


@application.errorhandler(ConflictError)  # type: ignore
def generate_conflict(error: ConflictError) -> dict:
    """
    This is the 409 response creator. It will create a 409 response along with
    a custom message and the 409 code

    :param error: The error body
    :return: Returns the response formatted
    """

    return generate_error_json(error, 409)
