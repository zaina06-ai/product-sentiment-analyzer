from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ScrapedReview:
    product_name: str
    product_image: str | None
    product_url: str | None
    brand: str | None
    rating: float | None
    review_title: str | None
    review_description: str | None
    review_rating: float | None
    reviewer_name: str | None
    review_date: Any | None
    verified_purchase: bool
    helpful_votes: int


class BaseScraper:
    platform: str

    def __init__(self, driver, *, max_pages: int = 3, retry_count: int = 3):
        self.driver = driver
        self.max_pages = int(max_pages)
        self.retry_count = int(retry_count)

    def _fetch_page(self, url: str) -> str:
        last_err: Exception | None = None
        for _ in range(self.retry_count):
            try:
                self.driver.get(url)
                time.sleep(1)
                return self.driver.page_source
            except Exception as e:  # Selenium errors
                last_err = e
                time.sleep(2)
        raise RuntimeError(f"Failed to fetch page after retries: {url}") from last_err

    def parse_reviews(self, html: str) -> List[ScrapedReview]:
        raise NotImplementedError

    def scrape(self, query_url: str) -> Iterable[ScrapedReview]:
        # Base strategy: iterate over pages by just fetching query_url.
        # Platform-specific implementation should override.
        html = self._fetch_page(query_url)
        yield from self.parse_reviews(html)

