from __future__ import annotations

from functools import wraps
from typing import Callable, Optional

from flask import request, jsonify

from utils.jwt_utils import decode_access_token

import jwt


def jwt_required(*, roles: Optional[list[str]] = None):
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"success": False, "message": "Invalid Token", "data": {}, "errors": None}), 401

            token = auth_header.split("Bearer ", 1)[1].strip()
            try:
                claims = decode_access_token(token)
            except jwt.ExpiredSignatureError:
                return (
                    jsonify({"success": False, "message": "Expired Token", "data": {}, "errors": None}),
                    401,
                )
            except Exception:
                return jsonify({"success": False, "message": "Invalid Token", "data": {}, "errors": None}), 401

            request.jwt_claims = claims  # type: ignore[attr-defined]

            role = claims.get("role")
            if roles is not None and role not in roles:
                return jsonify({"success": False, "message": "Forbidden", "data": {}, "errors": None}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator

