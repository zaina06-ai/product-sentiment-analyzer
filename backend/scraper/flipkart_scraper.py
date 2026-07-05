from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper, ScrapedReview


class FlipkartScraper(BaseScraper):
    platform = "flipkart"

    def parse_reviews(self, html: str) -> List[ScrapedReview]:
        soup = BeautifulSoup(html, "html.parser")
        reviews: List[ScrapedReview] = []

        # Generic Flipkart selectors
        for block in soup.select("div._2g7d2j"):
            title_el = block.select_one("div._2w3f7p")
            rating_el = block.select_one("div._3LWZlK")
            desc_el = block.select_one("div.col") or block.select_one("div._3wU53n")

            reviewer_el = block.select_one("div._2sc7ZR")
            date_el = block.select_one("p._1x7ZE9")

            reviews.append(
                ScrapedReview(
                    product_name="unknown",
                    product_image=None,
                    product_url=None,
                    brand=None,
                    rating=None,
                    review_title=title_el.text.strip() if title_el else None,
                    review_description=desc_el.text.strip() if desc_el else None,
                    review_rating=None,
                    reviewer_name=reviewer_el.text.strip() if reviewer_el else None,
                    review_date=date_el.text.strip() if date_el else None,
                    verified_purchase=False,
                    helpful_votes=0,
                )
            )

        return reviews

