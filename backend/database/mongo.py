from __future__ import annotations

from flask import Flask, current_app

from pymongo import MongoClient


def init_mongo(app: Flask) -> None:
    from config import get_config

    cfg = get_config()
    if not cfg.MONGODB_URI:
        # Allow local startup without Mongo; endpoints that require DB will fail explicitly.
        app.extensions["mongo_client"] = None
        return

    client = MongoClient(cfg.MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Ping to verify connectivity
    client.admin.command("ping")

    app.extensions["mongo_client"] = client
    app.extensions["mongo_db"] = client[cfg.MONGODB_DB]


def get_db() -> object:
    client = current_app.extensions.get("mongo_client")
    db = current_app.extensions.get("mongo_db")
    if client is None or db is None:
        raise RuntimeError("MongoDB is not configured or not reachable")
    return db

