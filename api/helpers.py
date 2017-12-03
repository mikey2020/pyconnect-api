from flask import jsonify

def response_json(status_code, value):
    """ helps send a json response """
    response = jsonify(value)
    response.status_code = status_code
    return response