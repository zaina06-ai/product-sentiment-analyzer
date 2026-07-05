from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: str = "User"
    created_at: datetime = datetime.now(timezone.utc)

    def to_mongo(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "created_at": self.created_at,
        }

