from flask import jsonify


def Success(message) -> dict:
    """
    :param message: The message to send
    :return: Returns a json response
    """
    status_code = 200
    json = {"success": True, "message": message, "code": status_code}
    resp = jsonify(json)
    resp.status_code = status_code

    return resp


def SuccessOutput(key, output) -> dict:
    """
    :param key: The key of the output
    :param output: The content of key

    :return: Returns a json response
    """
    status_code = 200
    json = {"success": True, key: output, "code": status_code}
    resp = jsonify(json)
    resp.status_code = status_code

    return resp


def SuccessOutputMessage(key, output, message) -> dict:
    """
    :param key: The key of the output
    :param output: The content of key
    :param message: A message

    :return: Returns a json response
    """
    status_code = 200
    json = {"message": message, "success": True, key: output, "code": status_code}
    resp = jsonify(json)
    resp.status_code = status_code

    return resp
