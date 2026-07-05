from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any, Dict, List

from database.repositories import get_latest_reviews, get_reviews_by_product_id


def _safe_float(x) -> float | None:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def compute_dashboard(product_id: str) -> Dict[str, Any]:
    reviews = get_reviews_by_product_id(product_id)
    if not reviews:
        return {
            "total_reviews": 0,
            "positive_reviews": 0,
            "negative_reviews": 0,
            "neutral_reviews": 0,
            "average_rating": None,
            "average_sentiment": None,
            "rating_distribution": {},
            "sentiment_distribution": {},
            "keyword_frequency": {},
            "most_positive_review": None,
            "most_negative_review": None,
            "latest_reviews": [],
            "review_timeline": [],
        }

    total = len(reviews)

    positive = sum(1 for r in reviews if r.get("sentiment", {}).get("positive", 0) >= max(r.get("sentiment", {}).get("negative", 0), r.get("sentiment", {}).get("neutral", 0)))
    negative = sum(1 for r in reviews if r.get("sentiment", {}).get("negative", 0) >= max(r.get("sentiment", {}).get("positive", 0), r.get("sentiment", {}).get("neutral", 0)))
    neutral = total - positive - negative

    ratings = [
        _safe_float(r.get("review_rating"))
        for r in reviews
        if _safe_float(r.get("review_rating")) is not None
    ]
    avg_rating = mean(ratings) if ratings else None

    compounds = [
        _safe_float(r.get("sentiment", {}).get("compound_score"))
        for r in reviews
        if _safe_float(r.get("sentiment", {}).get("compound_score")) is not None
    ]
    avg_sentiment = mean(compounds) if compounds else None

    rating_distribution = Counter(int(r.get("review_rating")) for r in reviews if r.get("review_rating") is not None)
    sentiment_distribution = Counter(
        max([("positive", r.get("sentiment", {}).get("positive", 0)), ("negative", r.get("sentiment", {}).get("negative", 0)), ("neutral", r.get("sentiment", {}).get("neutral", 0))], key=lambda x: x[1])[0]
        for r in reviews
    )

    # Very light keyword frequency from titles/descriptions
    keywords = Counter()
    for r in reviews:
        text = (r.get("review_title") or "") + " " + (r.get("review_description") or "")
        for w in text.lower().split():
            w = "".join(ch for ch in w if ch.isalnum())
            if len(w) >= 4:
                keywords[w] += 1

    latest = get_latest_reviews(product_id, limit=10)

    # Most positive/negative by compound_score
    most_pos = max(reviews, key=lambda r: r.get("sentiment", {}).get("compound_score", -1e9))
    most_neg = min(reviews, key=lambda r: r.get("sentiment", {}).get("compound_score", 1e9))

    # Timeline: group by review_date string (if present)
    timeline = []
    for r in sorted(reviews, key=lambda x: x.get("created_at"), reverse=False):
        timeline.append({"review_id": str(r.get("id")), "compound_score": r.get("sentiment", {}).get("compound_score")})

    return {
        "total_reviews": total,
        "positive_reviews": positive,
        "negative_reviews": negative,
        "neutral_reviews": neutral,
        "average_rating": avg_rating,
        "average_sentiment": avg_sentiment,
        "rating_distribution": dict(rating_distribution),
        "sentiment_distribution": dict(sentiment_distribution),
        "keyword_frequency": dict(keywords.most_common(20)),
        "most_positive_review": most_pos,
        "most_negative_review": most_neg,
        "latest_reviews": latest,
        "review_timeline": timeline[-50:],
    }

