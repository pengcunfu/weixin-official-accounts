from flask import jsonify


def success(data=None, message='success', code=200):
    response = {
        'code': code,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)


def error(message='fail', code=500, data=None):
    response = {
        'code': code,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)
