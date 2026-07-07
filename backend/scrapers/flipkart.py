"""
scrapers/flipkart.py
Flipkart search + review scraping. Selectors are best-effort — Flipkart
changes class names often, so this is written to fail soft rather than
crash (see base.ScrapeError).
"""

from .base import get, soup_from_html, extract_leaf_text_blocks, assert_not_block_page, ScrapeError
from preprocessing import extract_reviews_with_meta

BASE_URL = "https://www.flipkart.com"


def search_product(query: str) -> dict:
    html = get(f"{BASE_URL}/search", params={"q": query})
    assert_not_block_page(html, "Flipkart")
    soup = soup_from_html(html)

    anchor = None
    for a in soup.find_all("a", href=True):
        if "/p/" in a["href"]:
            anchor = a
            break

    if anchor is None:
        raise ScrapeError(
            "Couldn't find any product results on Flipkart. It may have "
            "changed its layout, or blocked this request."
        )

    product_url = anchor["href"]
    if product_url.startswith("/"):
        product_url = BASE_URL + product_url

    container = anchor
    for _ in range(3):
        if container.parent:
            container = container.parent

    name = anchor.get("title") or query
    img_tag = container.find("img")
    image = img_tag["src"] if img_tag and img_tag.get("src") else None
    price_tag = container.find(string=lambda s: s and s.strip().startswith("\u20b9"))
    price = price_tag.strip() if price_tag else None

    return {"name": name, "url": product_url, "image": image, "price": price}


def get_reviews(product_url: str, max_reviews: int = 30, max_pages: int = 3) -> list:
    """
    Flipkart's server-rendered HTML only includes ~10 reviews per page —
    the rest load via JS pagination we can't execute. To get closer to
    max_reviews, we fetch a few review pages (?page=2, ?page=3, ...) and
    pool all their raw text together before filtering, instead of
    filtering each page in isolation.
    """
    reviews_base = product_url.replace("/p/", "/product-reviews/")
    all_raw_texts = []

    for page in range(1, max_pages + 1):
        url = reviews_base if page == 1 else f"{reviews_base}&page={page}"
        try:
            html = get(url)
        except ScrapeError:
            if page == 1:
                raise
            break  # later pages may just not exist — stop quietly

        assert_not_block_page(html, "Flipkart")
        soup = soup_from_html(html)
        all_raw_texts.extend(extract_leaf_text_blocks(soup))

    reviews_all = extract_reviews_with_meta(all_raw_texts)
    reviews = reviews_all[:max_reviews]

    if not reviews:
        raise ScrapeError(
            "No reviews could be extracted after filtering. The product "
            "may have no reviews yet, or Flipkart's page structure changed."
        )

    return reviews
