from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from textblob import TextBlob


@dataclass(frozen=True)
class SentimentResult:
    positive: float
    negative: float
    neutral: float
    polarity: float
    subjectivity: float
    compound_score: float
    confidence_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "positive": self.positive,
            "negative": self.negative,
            "neutral": self.neutral,
            "polarity": self.polarity,
            "subjectivity": self.subjectivity,
            "compound_score": self.compound_score,
            "confidence_score": self.confidence_score,
        }


def analyze_text(text: str, *, use_vader: bool = True) -> SentimentResult:
    cleaned = (text or "").strip()

    # TextBlob
    blob = TextBlob(cleaned)
    polarity = float(blob.sentiment.polarity)
    subjectivity = float(blob.sentiment.subjectivity)

    # VADER (lazy import so nltk isn't required at import-time)
    compound_score = 0.0
    confidence_score = 0.0
    if use_vader:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(cleaned)
        compound_score = float(vs.get("compound", 0.0))
        # Map compound magnitude to a pseudo confidence
        confidence_score = min(1.0, abs(compound_score))

        # Derive positive/negative/neutral from probabilities
        pos = float(vs.get("pos", 0.0))
        neg = float(vs.get("neg", 0.0))
        neu = float(vs.get("neu", 0.0))
        positive, negative, neutral = pos, neg, neu
    else:
        # Fallback: use polarity
        positive = max(0.0, polarity)
        negative = max(0.0, -polarity)
        neutral = 1.0 - min(1.0, positive + negative)
        compound_score = polarity
        confidence_score = min(1.0, abs(polarity))

    return SentimentResult(
        positive=positive,
        negative=negative,
        neutral=neutral,
        polarity=polarity,
        subjectivity=subjectivity,
        compound_score=compound_score,
        confidence_score=confidence_score,
    )

