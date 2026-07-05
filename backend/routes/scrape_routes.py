from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, jsonify, request

from services.scraping_service import scrape_amazon, scrape_flipkart
from utils.input_validation import validate_product_name


scrape_bp = Blueprint("scrape_bp", __name__)


@scrape_bp.post("/amazon")
def scrape_amz():
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    product_name = body.get("product_name")
    query_url = body.get("query_url")
    max_pages = int(body.get("max_pages", 3))

    try:
        validated = validate_product_name(product_name)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e), "data": {}, "errors": None}), 422

    if not query_url:
        return jsonify({"success": False, "message": "query_url is required", "data": {}, "errors": None}), 400

    result = scrape_amazon(product_name=validated, query_url=query_url, max_pages=max_pages)
    return jsonify({"success": True, "message": "Scrape completed", "data": result, "errors": None}), 200


@scrape_bp.post("/flipkart")
def scrape_fk():
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    product_name = body.get("product_name")
    query_url = body.get("query_url")
    max_pages = int(body.get("max_pages", 3))

    try:
        validated = validate_product_name(product_name)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e), "data": {}, "errors": None}), 422

    if not query_url:
        return jsonify({"success": False, "message": "query_url is required", "data": {}, "errors": None}), 400

    result = scrape_flipkart(product_name=validated, query_url=query_url, max_pages=max_pages)
    return jsonify({"success": True, "message": "Scrape completed", "data": result, "errors": None}), 200

