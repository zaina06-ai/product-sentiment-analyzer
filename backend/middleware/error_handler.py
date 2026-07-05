from __future__ import annotations

import logging
from typing import Any, Dict

from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest, Forbidden, HTTPException, InternalServerError, NotFound, TooManyRequests, Unauthorized

logger = logging.getLogger(__name__)


def _response(success: bool, message: str, data: Dict[str, Any] | None = None, errors: Any = None, status_code: int = 200):
    payload = {
        "success": success,
        "message": message,
        "data": data or {},
        "errors": errors,
    }
    return jsonify(payload), status_code


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        logger.exception("HTTPException: %s", err)
        status_code = getattr(err, "code", 500) or 500

        if status_code == 400:
            return _response(False, "Bad Request", status_code=status_code)
        if status_code == 401:
            return _response(False, "Unauthorized", status_code=status_code)
        if status_code == 403:
            return _response(False, "Forbidden", status_code=status_code)
        if status_code == 404:
            return _response(False, "Not Found", status_code=status_code)
        if status_code == 429:
            return _response(False, "Too Many Requests", status_code=status_code)

        return _response(False, err.name or "Error", status_code=status_code)

    @app.errorhandler(TooManyRequests)
    def handle_too_many(err: TooManyRequests):
        return _response(False, "Too Many Requests", status_code=429)

    @app.errorhandler(BadRequest)
    def handle_bad_request(err: BadRequest):
        return _response(False, "Bad Request", errors=str(err), status_code=400)

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(err: Unauthorized):
        return _response(False, "Unauthorized", errors=str(err), status_code=401)

    @app.errorhandler(Forbidden)
    def handle_forbidden(err: Forbidden):
        return _response(False, "Forbidden", errors=str(err), status_code=403)

    @app.errorhandler(NotFound)
    def handle_not_found(err: NotFound):
        return _response(False, "Not Found", errors=str(err), status_code=404)

    @app.errorhandler(InternalServerError)
    def handle_500(err: InternalServerError):
        logger.exception("InternalServerError: %s", err)
        return _response(False, "Internal Server Error", status_code=500)

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        logger.exception("Unhandled exception: %s", err)
        return _response(False, "Internal Server Error", errors=str(err), status_code=500)

