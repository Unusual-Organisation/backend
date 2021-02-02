from flask import jsonify


def SuccessCreated(message: str) -> dict:
    """
    Will generate a SuccessCreated message with the appropriate return code and jsonify it.

    :param message: The message to include

    :return: Returns a json response
    """

    status_code = 201
    success = True
    json = {"success": success, "message": message, "code": status_code}
    resp = jsonify(json)
    resp.status_code = status_code

    return resp
