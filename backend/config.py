from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class Config:
    # Flask
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "0") == "1"

    # Mongo
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "product_sentiment")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "product-sentiment-backend")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "product-sentiment-client")
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60")
    )

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

    # Simple in-memory rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "200"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Selenium
    SELENIUM_HEADLESS: bool = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
    SELENIUM_PAGELOAD_TIMEOUT_SECONDS: int = int(
        os.getenv("SELENIUM_PAGELOAD_TIMEOUT_SECONDS", "30")
    )
    SELENIUM_IMPLICIT_WAIT_SECONDS: int = int(os.getenv("SELENIUM_IMPLICIT_WAIT_SECONDS", "5"))
    SELENIUM_RETRY_COUNT: int = int(os.getenv("SELENIUM_RETRY_COUNT", "3"))

    @property
    def jwt_access_token_expires_timedelta(self) -> timedelta:
        return timedelta(minutes=self.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)


def get_config() -> Config:
    return Config()

