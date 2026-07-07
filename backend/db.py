"""
db.py
Thin MongoDB caching layer. If MongoDB isn't reachable (not installed,
wrong URI, Atlas cluster paused, etc.), every function here fails soft —
the app keeps working, it just scrapes fresh every time instead of
serving from cache. Nothing here should ever crash the API.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

load_dotenv()  # loaded here too, so this module works even if imported first

CACHE_TTL_HOURS = 6

_db = None
_connection_attempted = False


def get_db():
    """Lazily connects to MongoDB. Returns None if unavailable."""
    global _db, _connection_attempted

    if _db is not None:
        return _db
    if _connection_attempted:
        # We already tried once and failed this run — don't retry on
        # every request, that would slow every search down.
        return None

    _connection_attempted = True

    # Read env vars here (not at module import time) so this always
    # reflects whatever .env was actually loaded, regardless of import order.
    mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.environ.get("MONGODB_DB", "sentiscrap")

    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")  # forces a real connection check

        db = client[db_name]
        db.searches.create_index([("query", ASCENDING)], unique=True)
        db.searches.create_index(
            [("cached_at", ASCENDING)], expireAfterSeconds=CACHE_TTL_HOURS * 3600
        )
        _db = db
        print("[db] Connected to MongoDB — caching enabled.")
        return _db
    except PyMongoError as e:
        print(f"[db] MongoDB unavailable, running without cache ({e})")
        return None


def _normalize(query: str) -> str:
    return query.lower().strip()


def get_cached_result(query: str):
    """Returns a previously cached search result dict, or None."""
    db = get_db()
    if db is None:
        return None
    try:
        doc = db.searches.find_one({"query": _normalize(query)})
        if not doc:
            return None
        doc.pop("_id", None)
        doc.pop("cached_at", None)
        doc.pop("query", None)
        return doc
    except PyMongoError as e:
        print(f"[db] read failed, ignoring cache ({e})")
        return None


def save_result(query: str, data: dict):
    """Saves/overwrites the cached result for a query. Best-effort."""
    db = get_db()
    if db is None:
        return
    try:
        doc = {**data, "query": _normalize(query), "cached_at": datetime.utcnow()}
        db.searches.update_one(
            {"query": _normalize(query)},
            {"$set": doc},
            upsert=True,
        )
    except PyMongoError as e:
        print(f"[db] write failed, continuing without caching this result ({e})")
