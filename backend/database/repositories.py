from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flask import current_app

from database.mongo import get_db


def _ensure_indexes() -> None:
    db = get_db()
    users = db["users"]
    products = db["products"]
    reviews = db["reviews"]
    analytics = db["analytics"]

    users.create_index("email", unique=True)
    products.create_index([("name", 1), ("source", 1)], unique=True)
    reviews.create_index([("product_id", 1), ("platform", 1), ("product_url", 1)], unique=True)
    reviews.create_index("product_id")
    reviews.create_index("created_at")
    analytics.create_index("product_id", unique=True)
    analytics.create_index("created_at")


def init_repositories() -> None:
    _ensure_indexes()


def create_user(*, email: str, password_hash: str, role: str) -> Dict[str, Any]:
    db = get_db()
    users = db["users"]
    user = {
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now(timezone.utc),
    }
    res = users.insert_one(user)
    return {"id": str(res.inserted_id), **user}


def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    user = db["users"].find_one({"email": email})
    if not user:
        return None
    user["id"] = str(user.pop("_id"))
    return user


def upsert_product(name: str, source: str) -> Dict[str, Any]:
    db = get_db()
    products = db["products"]

    now = datetime.now(timezone.utc)
    res = products.update_one(
        {"name": name, "source": source},
        {"$setOnInsert": {"name": name, "source": source, "created_at": now}},
        upsert=True,
    )

    # Fetch the document
    doc = products.find_one({"name": name, "source": source})
    doc["id"] = str(doc.pop("_id"))
    return doc


def insert_review(review: Dict[str, Any]) -> bool:
    """Insert review. Returns True if inserted, False if duplicate."""
    db = get_db()
    reviews = db["reviews"]

    try:
        res = reviews.insert_one(review)
        return bool(res.inserted_id)
    except Exception as e:
        # Duplicate key errors surface as generic exceptions depending on driver.
        # We'll detect by message.
        if "duplicate" in str(e).lower():
            return False
        raise


def find_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    doc = db["products"].find_one({"_id": product_id})
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


def get_product_list(limit: int = 50) -> List[Dict[str, Any]]:
    db = get_db()
    docs = db["products"].find({}).sort("created_at", -1).limit(int(limit))
    out: List[Dict[str, Any]] = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


def get_reviews_by_product_id(product_id: str) -> List[Dict[str, Any]]:
    db = get_db()
    docs = db["reviews"].find({"product_id": product_id}).sort("created_at", -1)
    out: List[Dict[str, Any]] = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


def get_latest_reviews(product_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    db = get_db()
    docs = db["reviews"].find({"product_id": product_id}).sort("created_at", -1).limit(int(limit))
    out: List[Dict[str, Any]] = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out

