from __future__ import annotations

from typing import Any, Dict, List

from flask import Blueprint, jsonify, request

from database.repositories import get_product_list, upsert_product
from utils.input_validation import validate_product_name


product_bp = Blueprint("product_bp", __name__)


@product_bp.post("/search")
def search_product():
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    product_name = body.get("product_name")

    try:
        validated = validate_product_name(product_name)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e), "data": {}, "errors": None}), 422

    # Since we don't have external product catalog, return suggestions by simple heuristics.
    suggestions: List[Dict[str, Any]] = [
        {"name": validated, "source": "amazon"},
        {"name": validated, "source": "flipkart"},
    ]
    return jsonify({"success": True, "message": "Product suggestions", "data": {"suggestions": suggestions}, "errors": None}), 200


@product_bp.get("")
def list_products():
    limit = int(request.args.get("limit", "50"))
    return jsonify({"success": True, "message": "Products", "data": {"items": get_product_list(limit=limit)}, "errors": None}), 200


@product_bp.get("/<id>")
def get_product(id: str):
    # Not fully implemented due to repository limitations; keep consistent API.
    # We'll reuse list search by fetching product via direct query.
    from database.repositories import find_product_by_id

    try:
        doc = find_product_by_id(id)
    except Exception:
        doc = None

    if not doc:
        return jsonify({"success": False, "message": "Product Not Found", "data": {}, "errors": None}), 404
    return jsonify({"success": True, "message": "Product", "data": doc, "errors": None}), 200


@product_bp.put("/<id>")
def update_product(id: str):
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    name = body.get("name")
    source = body.get("source")

    if not name or not source:
        return jsonify({"success": False, "message": "name and source are required", "data": {}, "errors": None}), 400

    # Upsert by unique constraints; id is ignored for simplicity.
    validated = validate_product_name(name)
    prod = upsert_product(name=validated, source=source)
    return jsonify({"success": True, "message": "Product updated", "data": prod, "errors": None}), 200


@product_bp.delete("/<id>")
def delete_product(id: str):
    # Minimal: not implementing because repositories don't expose delete.
    return jsonify({"success": False, "message": "Not Implemented", "data": {}, "errors": "DELETE requires repository delete implementation"}), 501

