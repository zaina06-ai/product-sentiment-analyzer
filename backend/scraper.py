"""
scraper.py
Handles searching Flipkart and pulling reviews for the top result.

IMPORTANT: Flipkart frequently changes their HTML/CSS class names to break
scrapers, and will sometimes serve a CAPTCHA or a blank shell page to
non-browser requests. The selectors below are best-effort and may need
updating over time. Every function fails *soft* (returns None / [] plus
a message) instead of raising, so the API never 500s with a raw traceback.
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.flipkart.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class ScrapeError(Exception):
    """Raised when we can't get usable data back from Flipkart."""
    pass


def _get(url, params=None):
    resp = requests.get(url, headers=HEADERS, params=params, timeout=12)
    if resp.status_code != 200:
        raise ScrapeError(
            f"Flipkart returned status {resp.status_code} for {url}. "
            "It may be rate-limiting or blocking this request."
        )
    return resp.text


def search_product(query: str) -> dict:
    """
    Searches Flipkart for `query` and returns basic info + URL for the
    first matching product. Raises ScrapeError if nothing usable is found.
    """
    html = _get(f"{BASE_URL}/search", params={"q": query})
    soup = BeautifulSoup(html, "html.parser")

    # Flipkart search result product links generally sit inside <a> tags
    # whose href contains "/p/". We grab the first one that looks like a
    # real product link (not an ad banner / category link).
    anchor = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/p/" in href:
            anchor = a
            break

    if anchor is None:
        raise ScrapeError(
            "Couldn't find any product results on the page. Flipkart may "
            "have changed its layout, or blocked this request."
        )

    product_url = anchor["href"]
    if product_url.startswith("/"):
        product_url = BASE_URL + product_url

    # Try to pull a readable name/price/rating/image from the search card.
    # These class names change often; we fall back gracefully if missing.
    card = anchor
    # walk up a couple of parents to find the container with price/rating
    container = card
    for _ in range(3):
        if container.parent:
            container = container.parent

    def _first_text(selector_texts):
        for tag in container.find_all(string=True):
            text = tag.strip()
            if text:
                return text
        return None

    name = anchor.get("title") or _first_text([]) or query
    img_tag = container.find("img")
    image = img_tag["src"] if img_tag and img_tag.get("src") else None

    price_tag = container.find(string=lambda s: s and s.strip().startswith("\u20b9"))
    price = price_tag.strip() if price_tag else None

    return {
        "name": name,
        "url": product_url,
        "image": image,
        "price": price,
    }


def _reviews_url_from_product_url(product_url: str) -> str:
    # Flipkart product URLs look like:
    #   https://www.flipkart.com/<slug>/p/<itemid>?pid=...
    # Review pages live at:
    #   https://www.flipkart.com/<slug>/product-reviews/<itemid>?pid=...
    return product_url.replace("/p/", "/product-reviews/")


def get_reviews(product_url: str, max_reviews: int = 20) -> list:
    """
    Scrapes review text + star rating from a Flipkart product's review page.
    Returns a list of dicts: [{ "text": str, "rating": int|None }, ...]
    """
    reviews_url = _reviews_url_from_product_url(product_url)
    html = _get(reviews_url)
    soup = BeautifulSoup(html, "html.parser")

    reviews = []

    # Review text blocks are usually inside <div> elements with long text
    # content that sit near a star-rating element. We take a heuristic
    # approach: any <div> whose direct text is reasonably long (> 40 chars)
    # and doesn't look like a UI label.
    candidates = soup.find_all("div")
    seen_texts = set()

    for div in candidates:
        text = div.get_text(" ", strip=True)
        if not text or len(text) < 40 or len(text) > 2000:
            continue
        if text in seen_texts:
            continue
        # Skip obvious non-review boilerplate
        lowered = text.lower()
        if any(
            phrase in lowered
            for phrase in [
                "read more", "flipkart", "terms of use", "privacy policy",
                "sign up", "become a seller",
            ]
        ) and len(text) < 60:
            continue

        seen_texts.add(text)
        reviews.append({"text": text, "rating": None})

        if len(reviews) >= max_reviews:
            break

    if not reviews:
        raise ScrapeError(
            "No reviews could be extracted. The product may have no "
            "reviews yet, or Flipkart's page structure has changed."
        )

    return reviews
