"""
scrapers/base.py
Shared HTTP + extraction helpers for site-specific scraper modules.
"""

import requests
from bs4 import BeautifulSoup

from preprocessing import clean_review_candidates

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class ScrapeError(Exception):
    """Raised when we can't get usable data back from a site."""
    pass


def get(url, params=None):
    resp = requests.get(url, headers=HEADERS, params=params, timeout=12)
    if resp.status_code != 200:
        raise ScrapeError(
            f"Site returned status {resp.status_code} for {url}. "
            "It may be rate-limiting or blocking this request."
        )
    return resp.text


# Phrases that only ever show up on a sign-in / verification / captcha
# wall — never on a real product or review page. If a fetched page
# contains any of these, the site detected us as a bot and served a
# challenge page instead of real content. We must catch this BEFORE
# running text extraction, or this login-page text gets scraped and
# scored as if it were customer reviews.
BLOCK_PAGE_MARKERS = [
    "enter the characters you see",
    "conditions of use",
    "sign in with your password",
    "your passkey is not working",
    "something went wrong, please sign-in",
    "delete saved passkeys",
    "to discuss automated access",
    "enable javascript on your browser to continue",
    "type the characters you see in this image",
    "unusual traffic from your",
]


def assert_not_block_page(html: str, site_name: str):
    lowered = html.lower()
    if any(marker in lowered for marker in BLOCK_PAGE_MARKERS):
        raise ScrapeError(
            f"{site_name} served a sign-in/verification page instead of "
            "the real page — it detected this as automated traffic. "
            "This is Amazon/Flipkart's anti-bot protection, not a bug in "
            "the scraper's parsing. Try again later, use a different "
            "product, or switch source."
        )


def soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def extract_leaf_text_blocks(soup: BeautifulSoup) -> list:
    """
    Returns text from LEAF elements only — tags that don't themselves
    contain another <div>/<p> with text. This avoids the classic bug
    where a wrapper <div> around a whole review card gets scraped
    alongside its own children, duplicating text and pulling in
    surrounding nav/menu content that happens to sit in a parent
    container with the review.
    """
    raw_texts = []
    for tag in soup.find_all(["div", "p", "span", "li"]):
        if tag.find(["div", "p"]):
            # has nested block-level children with their own text — not a leaf
            continue
        text = tag.get_text(" ", strip=True)
        if text:
            raw_texts.append(text)
    return raw_texts


def extract_clean_reviews(soup: BeautifulSoup, max_reviews: int = 20) -> list:
    """
    Full pipeline: leaf extraction -> dedupe/boilerplate filtering ->
    cap to max_reviews. Returns list of {"text": str, "rating": None}.
    """
    raw_texts = extract_leaf_text_blocks(soup)
    cleaned = clean_review_candidates(raw_texts)

    return [{"text": t, "rating": None} for t in cleaned[:max_reviews]]
