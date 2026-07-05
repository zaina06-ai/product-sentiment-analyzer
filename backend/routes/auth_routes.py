from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, jsonify, request

from database.repositories import create_user, find_user_by_email
from middleware.auth_middleware import jwt_required
from utils.crypto import hash_password
from utils.jwt_utils import create_access_token


auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.post("/register")
def register():
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password")
    role = (body.get("role") or "User").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "email and password are required", "data": {}, "errors": None}), 400
    if len(password) < 8:
        return jsonify({"success": False, "message": "password must be at least 8 characters", "data": {}, "errors": None}), 422

    if find_user_by_email(email):
        return jsonify({"success": False, "message": "User already exists", "data": {}, "errors": None}), 409

    user = create_user(email=email, password_hash=hash_password(password), role=role if role in {"Admin", "User"} else "User")
    return jsonify({"success": True, "message": "User created", "data": {"id": user["id"], "email": user["email"], "role": user["role"]}, "errors": None}), 201


@auth_bp.post("/login")
def login():
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "email and password are required", "data": {}, "errors": None}), 400

    user = find_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials", "data": {}, "errors": None}), 401

    from utils.crypto import verify_password

    if not verify_password(password, user["password_hash"]):
        return jsonify({"success": False, "message": "Invalid credentials", "data": {}, "errors": None}), 401

    token = create_access_token(user_id=user["id"], role=user.get("role") or "User")
    return jsonify({"success": True, "message": "Login successful", "data": {"token": token}, "errors": None}), 200


@auth_bp.get("/profile")
@jwt_required()
def profile():
    claims = request.jwt_claims  # type: ignore[attr-defined]
    return jsonify({"success": True, "message": "Profile", "data": {"user_id": claims.get("sub"), "role": claims.get("role")}, "errors": None}), 200

