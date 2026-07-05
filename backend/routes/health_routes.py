from __future__ import annotations

from flask import Blueprint, jsonify

health_bp = Blueprint("health_bp", __name__)


@health_bp.get("/health")
def health():
    return jsonify({"success": True, "message": "OK", "data": {}, "errors": None}), 200

