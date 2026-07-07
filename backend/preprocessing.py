"""
preprocessing.py
Cleans the raw text blocks pulled off a product/review page before they
ever reach sentiment analysis. Three problems this solves:

1. Parent/child duplication: BeautifulSoup div-scraping often grabs a
   wrapper <div> AND the smaller <div>s inside it, so the same words
   appear multiple times at different "sizes". We keep only the most
   specific (leaf-most) version of any overlapping text.

2. Site chrome disguised as a review: nav bars, "Sign Up", "Become a
   Seller", rating-count summaries ("4,969 ratings and 199 reviews"),
   star breakdowns ("1 ★ 299 2 ★ 190..."), etc. are real text nodes on
   the page but are not reviews. We score text against a phrase
   blocklist + regex patterns and drop anything that matches.

3. Names and labels that LOOK like real content but aren't a review:
   a reviewer's byline ("Sheetla Prasad Maurya"), a footer address
   ("Clove Embassy Tech Village,"), a UI label ("Registered Office
   Address:"). These share a shape real review sentences don't: every
   word is Capitalized, and none of the words are ordinary sentence
   words (the, is, for, and, with, ...). We detect that shape directly
   instead of relying on a fixed phrase list, since addresses/names are
   effectively infinite in variety.
"""

import re

# Phrases that show up in site navigation/footers/menus, not in reviews.
# A block is rejected if it contains 2+ of these (a single incidental
# match, e.g. "cart" inside a real sentence, shouldn't kill a review) —
# UNLESS the phrase makes up most of the whole text, in which case one
# match is enough (see _is_dominant_phrase below).
BOILERPLATE_PHRASES = [
    "sign up", "log in", "login", "my profile", "wishlist",
    "become a seller", "notification preferences", "customer care",
    "advertise", "download app", "one-stop shopping", "wholesale prices",
    "flipkart plus", "flipkart cart", "add to cart", "buy now",
    "search icon", "new customer", "gift cards", "flipkart zone",
    "your travel needs", "track order", "return policy",
    "reviews sorted by", "loading content", "registered office address",
    "corporate identification", "customer support", "all rights reserved",
]

RATING_SUMMARY_RE = re.compile(r"[\d,]+\s*ratings?\b.{0,20}[\d,]+\s*reviews?\b", re.I)
STAR_BREAKDOWN_RE = re.compile(r"(\d\s*(?:★|\*|stars?)\s*[\d,]+\s*){2,}", re.I)

# Ordinary sentence words. If a short, all-Capitalized text contains
# NONE of these, it's almost certainly a proper-noun run (a person's
# name, a company/address fragment, a UI label in Title Case) rather
# than an actual opinion about a product.
COMMON_SENTENCE_WORDS = {
    "a", "an", "the", "is", "was", "are", "were", "am", "be", "been",
    "and", "or", "but", "for", "so", "if", "of", "in", "on", "at", "to",
    "with", "it", "its", "this", "that", "i", "my", "me", "we", "our",
    "you", "your", "not", "no", "very", "really", "too", "as", "than",
    "will", "would", "can", "could", "do", "does", "did", "has", "have",
    "had", "just", "all", "more", "most", "good", "bad", "best", "worst",
    "great", "nice", "love", "loving", "loved", "like", "liked",
}


def _is_dominant_phrase(lowered: str, phrase: str) -> bool:
    """True if `phrase` makes up most of the (short) text — e.g. the
    whole block IS the label "Notification Preferences", not a real
    sentence that happens to mention it in passing."""
    return phrase in lowered and len(phrase) / max(len(lowered), 1) > 0.6


def _boilerplate_hits(lowered: str) -> int:
    return sum(1 for phrase in BOILERPLATE_PHRASES if phrase in lowered)


def _looks_like_name_or_label(text: str) -> bool:
    """
    Flags short, all-Title-Case text with no ordinary sentence words —
    the shape of a person's name, an address fragment, or a UI label,
    as opposed to a real review sentence/title.
    """
    words = text.strip().rstrip(":,.").split()
    if not (1 <= len(words) <= 6):
        return False

    alpha_words = [w for w in words if w.isalpha()]
    if not alpha_words:
        return False

    all_capitalized = all(w[0].isupper() for w in alpha_words)
    if not all_capitalized:
        return False

    has_common_word = any(w.lower() in COMMON_SENTENCE_WORDS for w in words)
    return not has_common_word


DATE_RE = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s*\d{4}\b",
    re.I,
)


def dedupe_nested_ordered(raw_texts: list) -> list:
    """
    Same containment-dedup as dedupe_nested, but preserves original page
    order instead of sorting by length. Order matters here because we
    use position (a name/date block sitting right after a review body)
    to attach reviewer metadata to the right review.
    """
    unique_in_order = list(dict.fromkeys(raw_texts))  # dedupe exact, keep order
    result = []
    for text in unique_in_order:
        if any(text != other and text in other for other in unique_in_order):
            continue
        result.append(text)
    return result


def extract_reviews_with_meta(
    raw_texts: list, min_len: int = 15, max_len: int = 2000, lookahead: int = 3
) -> list:
    """
    Like clean_review_candidates, but also tries to attach the reviewer's
    name and date to each review by looking at the text block(s) that
    immediately follow it on the page. Flipkart typically renders each
    review as: [review title/body] [reviewer name, place] [date/Verified
    Purchase]. The name line would normally be dropped by
    _looks_like_name_or_label — here we deliberately capture it as
    metadata for the review right before it instead of just discarding it.

    Returns: list of {"text": str, "author": str|None, "date": str|None,
                       "rating": None}
    """
    ordered = dedupe_nested_ordered(raw_texts)
    reviews = []
    used_as_meta = set()

    for i, text in enumerate(ordered):
        if i in used_as_meta:
            continue
        if len(text) < min_len or len(text) > max_len:
            continue
        if is_boilerplate(text):
            continue
        if _looks_like_name_or_label(text):
            continue  # this block itself is a name/label, not a review

        author = None
        date = None

        for j in range(i + 1, min(i + 1 + lookahead, len(ordered))):
            if j in used_as_meta:
                continue
            candidate = ordered[j]

            if author is None and len(candidate) <= 60 and _looks_like_name_or_label(candidate):
                author = candidate.rstrip(":,.")
                used_as_meta.add(j)
                continue

            date_match = DATE_RE.search(candidate)
            if date is None and date_match and len(candidate) <= 60:
                date = date_match.group(0)
                used_as_meta.add(j)
                continue

            # Hit something that's neither a name nor a date — stop
            # looking ahead, it's likely the next review already.
            break

        reviews.append({"text": text, "author": author, "date": date, "rating": None})

    return reviews


def is_boilerplate(text: str) -> bool:
    lowered = text.lower()

    if RATING_SUMMARY_RE.search(text):
        return True
    if STAR_BREAKDOWN_RE.search(text):
        return True
    if any(_is_dominant_phrase(lowered, phrase) for phrase in BOILERPLATE_PHRASES):
        return True
    if _boilerplate_hits(lowered) >= 2:
        return True
    if _looks_like_name_or_label(text):
        return True
    return False


def dedupe_nested(candidates: list) -> list:
    """
    Drops any text block that fully contains another, shorter block
    already in the set — that's almost always a parent <div> that wraps
    several smaller real elements (nav sections, or a review + its
    surrounding card), not a genuine standalone block of its own.
    """
    unique_sorted = sorted(set(candidates), key=len)
    accepted = []
    for text in unique_sorted:
        if any(shorter != text and shorter in text for shorter in accepted):
            continue
        accepted.append(text)
    return accepted


def clean_review_candidates(raw_texts: list, min_len: int = 15, max_len: int = 2000) -> list:
    """
    Full pipeline: dedupe nested wrappers, drop boilerplate, drop
    anything outside a sane review-length range.
    """
    deduped = dedupe_nested(raw_texts)
    cleaned = []
    for text in deduped:
        if len(text) < min_len or len(text) > max_len:
            continue
        if is_boilerplate(text):
            continue
        cleaned.append(text)
    return cleaned
