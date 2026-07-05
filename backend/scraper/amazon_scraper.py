from __future__ import annotations

from typing import Any, List, Optional

from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper, ScrapedReview


class AmazonScraper(BaseScraper):
    platform = "amazon"

    def parse_reviews(self, html: str) -> List[ScrapedReview]:
        soup = BeautifulSoup(html, "html.parser")

        reviews: List[ScrapedReview] = []
        # Generic Amazon review block selectors (may change)
        for block in soup.select("div[data-hook='review']"):
            title_el = block.select_one("a[data-hook='review-title'] span")
            rating_el = block.select_one("i[data-hook='review-star-rating'] span")
            desc_el = block.select_one("div[data-hook='review-body'] span")
            reviewer_el = block.select_one("span.a-profile-name")
            date_el = block.select_one("span[data-hook='review-date']")
            verified_el = block.select_one("span[data-hook='avp-badge']")
            helpful_el = block.select_one("span[data-hook='helpful-vote-count']")

            review_rating = None
            if rating_el and rating_el.text:
                try:
                    review_rating = float(rating_el.text.strip().split()[0])
                except Exception:
                    review_rating = None

            helpful_votes = 0
            if helpful_el and helpful_el.text:
                try:
                    helpful_votes = int(helpful_el.text.strip())
                except Exception:
                    helpful_votes = 0

            reviews.append(
                ScrapedReview(
                    product_name="unknown",
                    product_image=None,
                    product_url=None,
                    brand=None,
                    rating=None,
                    review_title=title_el.text.strip() if title_el else None,
                    review_description=desc_el.text.strip() if desc_el else None,
                    review_rating=review_rating,
                    reviewer_name=reviewer_el.text.strip() if reviewer_el else None,
                    review_date=date_el.text.strip() if date_el else None,
                    verified_purchase=bool(verified_el),
                    helpful_votes=helpful_votes,
                )
            )

        return reviews

