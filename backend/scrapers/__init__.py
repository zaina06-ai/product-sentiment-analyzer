from . import flipkart
from .base import ScrapeError

SCRAPERS = {
    "flipkart": flipkart,
}


def get_scraper(site: str):
    site = (site or "flipkart").strip().lower()
    if site not in SCRAPERS:
        raise ValueError(f"Unsupported site: {site!r}. Only 'flipkart' is supported.")
    return SCRAPERS[site]
