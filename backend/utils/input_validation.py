from __future__ import annotations

import re
from typing import Optional


_ALLOWED_PRODUCT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\s\-\._]{0,100}$")
_INVALID_CHARS_RE = re.compile(r"[^A-Za-z0-9\s\-\._]")


def validate_product_name(name: Optional[str]) -> str:
    if name is None:
        raise ValueError("Product name is required")

    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Product name cannot be empty")

    if len(cleaned) > 120:
        raise ValueError("Product name is too long")

    if _INVALID_CHARS_RE.search(cleaned):
        raise ValueError("Product name contains invalid characters")

    # More strict allow-list (prevents odd punctuation)
    if not _ALLOWED_PRODUCT_NAME_RE.match(cleaned):
        raise ValueError("Product name format is invalid")

    return cleaned

