from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, jsonify

from services.analytics_service import compute_dashboard


dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.get("/<productId>")
def dashboard(productId: str):
    data = compute_dashboard(productId)
    if data.get("total_reviews", 0) == 0:
        return jsonify({"success": False, "message": "No Reviews", "data": {}, "errors": None}), 404
    return jsonify({"success": True, "message": "Dashboard", "data": data, "errors": None}), 200

