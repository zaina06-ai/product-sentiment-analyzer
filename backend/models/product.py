from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class Product:
    id: str
    name: str
    source: str | None = None
    created_at: datetime = datetime.now(timezone.utc)

    def to_mongo(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "created_at": self.created_at,
        }

