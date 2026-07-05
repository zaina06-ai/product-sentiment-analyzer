from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class Review:
    id: str
    product_id: str
    platform: str
    review_title: str | None
    review_description: str | None
    review_rating: float | None
    reviewer_name: str | None
    review_date: datetime | None
    verified_purchase: bool
    helpful_votes: int
    product_url: str | None
    product_image: str | None

    sentiment: Dict[str, Any]
    created_at: datetime = datetime.now(timezone.utc)

    def to_mongo(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "platform": self.platform,
            "review_title": self.review_title,
            "review_description": self.review_description,
            "review_rating": self.review_rating,
            "reviewer_name": self.reviewer_name,
            "review_date": self.review_date,
            "verified_purchase": self.verified_purchase,
            "helpful_votes": self.helpful_votes,
            "product_url": self.product_url,
            "product_image": self.product_image,
            "sentiment": self.sentiment,
            "created_at": self.created_at,
        }

