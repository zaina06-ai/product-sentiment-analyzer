"""
sentiment.py
Runs both TextBlob and VADER on review text and combines them into a
single label + score, plus aggregate stats for the whole review set.
"""

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_vader = SentimentIntensityAnalyzer()

POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05


def _label_from_score(score: float) -> str:
    if score >= POSITIVE_THRESHOLD:
        return "positive"
    if score <= NEGATIVE_THRESHOLD:
        return "negative"
    return "neutral"


def analyze_text(text: str) -> dict:
    """Returns per-review sentiment scores + combined label."""
    tb_polarity = TextBlob(text).sentiment.polarity
    vader_compound = _vader.polarity_scores(text)["compound"]

    # Simple average of both models' normalized scores (-1..1 range)
    combined = (tb_polarity + vader_compound) / 2

    return {
        "textblob_score": round(tb_polarity, 3),
        "vader_score": round(vader_compound, 3),
        "combined_score": round(combined, 3),
        "label": _label_from_score(combined),
    }


def analyze_reviews(reviews: list) -> dict:
    """
    reviews: list of {"text": str, "rating": int|None}
    Returns: {
        "reviews": [ {...review, **sentiment} ],
        "summary": {
            "positive": int, "neutral": int, "negative": int,
            "average_score": float,
            "total": int
        }
    }
    """
    analyzed = []
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    total_score = 0.0

    for review in reviews:
        result = analyze_text(review["text"])
        merged = {**review, **result}
        analyzed.append(merged)
        counts[result["label"]] += 1
        total_score += result["combined_score"]

    total = len(analyzed) or 1
    summary = {
        **counts,
        "total": len(analyzed),
        "average_score": round(total_score / total, 3),
    }

    return {"reviews": analyzed, "summary": summary}
