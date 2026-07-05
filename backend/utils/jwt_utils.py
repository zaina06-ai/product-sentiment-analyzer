from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jwt
from flask import current_app


def _get_cfg():
    from config import get_config

    return get_config()


def create_access_token(*, user_id: str, role: str) -> str:
    cfg = _get_cfg()
    if not cfg.JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not configured")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iss": cfg.JWT_ISSUER,
        "aud": cfg.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + cfg.jwt_access_token_expires_timedelta).timestamp()),
    }

    return jwt.encode(payload, cfg.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    cfg = _get_cfg()
    if not cfg.JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not configured")

    return jwt.decode(
        token,
        cfg.JWT_SECRET,
        algorithms=["HS256"],
        audience=cfg.JWT_AUDIENCE,
        issuer=cfg.JWT_ISSUER,
    )

