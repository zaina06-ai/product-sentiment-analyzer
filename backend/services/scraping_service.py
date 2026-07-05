from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from config import get_config
from database.repositories import insert_review, upsert_product
from scraper.amazon_scraper import AmazonScraper
from scraper.browser_factory import BrowserConfig, create_chrome_driver
from scraper.flipkart_scraper import FlipkartScraper
from sentiment.sentiment_analyzer import analyze_text

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScrapeRequest:
    platform: str
    product_query_url: str
    product_name: str
    max_pages: int = 3


def scrape_amazon(*, product_name: str, query_url: str, max_pages: int = 3) -> Dict[str, Any]:
    cfg = get_config()
    driver = create_chrome_driver(
        config=BrowserConfig(
            headless=cfg.SELENIUM_HEADLESS,
            page_load_timeout_seconds=cfg.SELENIUM_PAGELOAD_TIMEOUT_SECONDS,
            implicit_wait_seconds=cfg.SELENIUM_IMPLICIT_WAIT_SECONDS,
        )
    )

    try:
        scraper = AmazonScraper(driver, max_pages=max_pages, retry_count=cfg.SELENIUM_RETRY_COUNT)
        product = upsert_product(name=product_name, source="amazon")
        product_id = product["id"]

        inserted = 0
        scraped = 0

        for r in scraper.scrape(query_url):
            scraped += 1
            sentiment = analyze_text(
                r.review_description or r.review_title or "",
                use_vader=True,
            ).to_dict()

            review_doc = {
                "product_id": product_id,
                "platform": "amazon",
                "review_title": r.review_title,
                "review_description": r.review_description,
                "review_rating": r.review_rating,
                "reviewer_name": r.reviewer_name,
                "review_date": r.review_date,
                "verified_purchase": r.verified_purchase,
                "helpful_votes": r.helpful_votes,
                "product_url": r.product_url,
                "product_image": r.product_image,
                "sentiment": sentiment,
            }

            if insert_review(review_doc):
                inserted += 1

        return {"scraped": scraped, "inserted": inserted}
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def scrape_flipkart(*, product_name: str, query_url: str, max_pages: int = 3) -> Dict[str, Any]:
    cfg = get_config()
    driver = create_chrome_driver(
        config=BrowserConfig(
            headless=cfg.SELENIUM_HEADLESS,
            page_load_timeout_seconds=cfg.SELENIUM_PAGELOAD_TIMEOUT_SECONDS,
            implicit_wait_seconds=cfg.SELENIUM_IMPLICIT_WAIT_SECONDS,
        )
    )

    try:
        scraper = FlipkartScraper(driver, max_pages=max_pages, retry_count=cfg.SELENIUM_RETRY_COUNT)
        product = upsert_product(name=product_name, source="flipkart")
        product_id = product["id"]

        inserted = 0
        scraped = 0

        for r in scraper.scrape(query_url):
            scraped += 1
            sentiment = analyze_text(
                r.review_description or r.review_title or "",
                use_vader=True,
            ).to_dict()

            review_doc = {
                "product_id": product_id,
                "platform": "flipkart",
                "review_title": r.review_title,
                "review_description": r.review_description,
                "review_rating": r.review_rating,
                "reviewer_name": r.reviewer_name,
                "review_date": r.review_date,
                "verified_purchase": r.verified_purchase,
                "helpful_votes": r.helpful_votes,
                "product_url": r.product_url,
                "product_image": r.product_image,
                "sentiment": sentiment,
            }

            if insert_review(review_doc):
                inserted += 1

        return {"scraped": scraped, "inserted": inserted}
    finally:
        try:
            driver.quit()
        except Exception:
            pass

