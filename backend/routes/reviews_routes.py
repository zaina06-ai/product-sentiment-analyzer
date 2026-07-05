from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, jsonify

from database.repositories import get_reviews_by_product_id


reviews_bp = Blueprint("reviews_bp", __name__)


@reviews_bp.get("/<productId>")
def list_reviews(productId: str):
    reviews = get_reviews_by_product_id(productId)
    if not reviews:
        return jsonify({"success": False, "message": "No Reviews", "data": {}, "errors": None}), 404
    return jsonify({"success": True, "message": "Reviews", "data": {"items": reviews}, "errors": None}), 200

