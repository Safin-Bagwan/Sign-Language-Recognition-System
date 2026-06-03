from flask import jsonify


def success(data=None, status_code=200):
    payload = {"ok": True}
    if data:
        payload.update(data)
    return jsonify(payload), status_code


def error(message, status_code=400, code="bad_request", details=None):
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status_code
