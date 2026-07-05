from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from database.mongo import init_mongo
from middleware.error_handler import register_error_handlers
from middleware.security_headers import enable_security_headers
from middleware.rate_limiter import RateLimiter
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.scrape_routes import scrape_bp
from routes.reviews_routes import reviews_bp
from routes.dashboard_routes import dashboard_bp
from routes.health_routes import health_bp
from swagger.swagger_routes import swagger_bp


def create_app() -> Flask:
    load_dotenv()
    cfg = get_config()

    app = Flask(__name__)

    # Logging
    log_level = os.getenv("LOG_LEVEL", cfg.LOG_LEVEL).upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": cfg.CORS_ORIGINS.split(",")}},
    )

    # Mongo
    init_mongo(app)

    # Middleware
    enable_security_headers(app)
    RateLimiter(app, request_limit=cfg.RATE_LIMIT_REQUESTS, window_seconds=cfg.RATE_LIMIT_WINDOW_SECONDS)
    register_error_handlers(app)

    # Blueprints
    app.register_blueprint(swagger_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(product_bp, url_prefix="/api/product")
    app.register_blueprint(scrape_bp, url_prefix="/api/scrape")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    @app.get("/")
    def root():
        return jsonify({"success": True, "message": "Backend is running", "data": {}, "errors": None})

    return app


app = create_app()


if __name__ == "__main__":
    cfg = get_config()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(cfg.FLASK_DEBUG))

