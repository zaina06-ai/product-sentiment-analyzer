
import os
import re
import sys
import time
import hashlib
import unicodedata
import functools
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, TypeVar
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

import logging

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError, ConnectionFailure, PyMongoError

from tqdm import tqdm


# --- Configuration and Logging (from app_config/settings.py and config.py) ---

# Load environment variables from .env file at project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Directory paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

for directory in (RAW_DATA_DIR, PROCESSED_DATA_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# MongoDB Atlas configuration
MONGODB_URI: str = os.getenv("MONGODB_URI", "")
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "product_sentiment")
MONGO_COLLECTION_NAME: str = os.getenv("MONGO_COLLECTION_NAME", "reviews")

# Scraper configuration
FLIPKART_BASE_URL: str = "https://www.flipkart.com"
EXPLICIT_WAIT_TIMEOUT: int = int(os.getenv("EXPLICIT_WAIT_TIMEOUT", "15"))
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
HEADLESS: bool = os.getenv("HEADLESS", "True").strip().lower() in ("1", "true", "yes")
MAX_REVIEW_PAGES: int = int(os.getenv("MAX_REVIEW_PAGES", "5000"))

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger

logger = get_logger(__name__)

# Flipkart selectors (from app_config/settings.py)
SEARCH_BOX_SELECTORS = [
    "input[name='q']",
    "input.Pke_EE",
]
LOGIN_POPUP_CLOSE_SELECTORS = [
    "button._2KpZ6l._2doB4z",
    "button[class*='_2KpZ6l']",
]
FIRST_PRODUCT_SELECTORS = [
    "a[href*='/p/']",
    "a.CGtC98",
    "a.wjcEIp",
    "a._1fQZEK",
    "a.s1Q9rs",
    "div._4rR01T",
    "a.IRpwTa",
]
REVIEWS_SECTION_SELECTORS = [
    "div._3UAT2v span",
    "a.col.JOpGWQ",
    "a[href*='product-reviews']",
]
ALL_REVIEWS_LINK_SELECTORS = [
    "a[href*='product-reviews']",
    "div._3UAT2v",
    "a.col.JOpGWQ",
]
REVIEW_CARD_SELECTORS = [
    "div.col.EPCmJX",
    "div._27M-vq",
    "div.cPHDOP.col-12-12",
    "div[class*='review']",
]
REVIEW_TITLE_SELECTORS = ["p._2-N8zT", "p[class*='title']"]
REVIEW_TEXT_SELECTORS = ["div.ZmyHeo", "div.t-ZTKy", "div[class*='text']", "div.row div.ZmyHeo", "div._6K-7Co"]
REVIEW_RATING_SELECTORS = ["div._3LWZlK", "div.XQDdHH", "div[class*='rating']"]
REVIEW_DATE_SELECTORS = ["p._2NsDsF", "p[class*='date']"]
REVIEWER_NAME_SELECTORS = ["p._2NsDsF.AwS1CA", "p.AwS1CA"]
VERIFIED_PURCHASE_SELECTORS = ["p._2mcZGG span", "span.MCEcvi"]
NEXT_PAGE_SELECTORS = [
    "a._9QVEpD",
    "nav a[rel='next']",
    "a[href*='page=']",
]
GENERIC_CLOSE_BUTTON_SELECTORS = [
    "button._2KpZ6l._2doB4z",
    "button._30XB9F",
]


# --- Data Models (from database/models.py) ---

@dataclass
class Review:
    product_name: str
    review_title: str
    review_text: str
    rating: Optional[int]
    review_date_raw: str
    reviewer_name: str
    verified_purchase: bool
    product_url: str
    scraped_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def content_hash(self) -> str:
        key = f"{self.review_text.strip().lower()}|{self.review_date_raw.strip().lower()}|{self.product_name.strip().lower()}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()


# --- Selenium Utilities (from scraper/utils.py) ---

T = TypeVar("T")

def build_driver() -> WebDriver:
    logger.info("Initialising Chrome WebDriver (headless=%s)", HEADLESS)
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if os.path.exists("/usr/bin/chromium") and os.path.exists("/home/ubuntu/.wdm/drivers/chromedriver/linux64/148.0.7778.178/chromedriver-linux64/chromedriver"):
        options.binary_location = "/usr/bin/chromium"
        service = Service(executable_path="/home/ubuntu/.wdm/drivers/chromedriver/linux64/148.0.7778.178/chromedriver-linux64/chromedriver")
    else:
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(0)
    logger.info("Chrome WebDriver initialised successfully")
    return driver

def _dump_failure_artifacts(driver: Optional[WebDriver], func_name: str) -> None:
    if driver is None:
        return
    try:
        os.makedirs("logs", exist_ok=True)
        screenshot_path = f"logs/failure_{func_name}.png"
        html_path = f"logs/failure_{func_name}.html"
        driver.save_screenshot(screenshot_path)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.error(
            "Saved failure screenshot (%s) and page source (%s) for debugging.",
            screenshot_path,
            html_path,
        )
    except Exception as exc:
        logger.debug("Could not save failure artifacts: %s", exc)

def retry_on_exception(
    exceptions: tuple = (StaleElementReferenceException, TimeoutException),
    retries: int = MAX_RETRIES,
    delay: float = 1.0,
) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Optional[Exception] = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    logger.warning(
                        "Attempt %d/%d failed for %s: %s",
                        attempt,
                        retries,
                        func.__name__,
                        exc.__class__.__name__,
                    )
                    time.sleep(delay)
            logger.error(
                "All %d retries exhausted for %s", retries, func.__name__
            )
            try:
                driver = getattr(args[0], "driver", None) if args else None
                _dump_failure_artifacts(driver, func.__name__)
            except Exception:
                pass
            raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator

def wait_for_any(
    driver: WebDriver, selectors: List[str], timeout: int = EXPLICIT_WAIT_TIMEOUT
) -> WebElement:
    last_exception: Optional[Exception] = None
    for selector in selectors:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException as exc:
            last_exception = exc
            continue
    logger.debug("None of the selectors matched: %s", selectors)
    raise last_exception or TimeoutException(f"No selector matched: {selectors}")

def find_first(
    parent, selectors: List[str], by: By = By.CSS_SELECTOR
) -> Optional[WebElement]:
    for selector in selectors:
        try:
            return parent.find_element(by, selector)
        except NoSuchElementException:
            continue
    return None

def find_all_first(
    parent, selectors: List[str], by: By = By.CSS_SELECTOR
) -> List[WebElement]:
    for selector in selectors:
        elements = parent.find_elements(by, selector)
        if elements:
            return elements
    return []

def safe_text(element: Optional[WebElement], default: str = "") -> str:
    if element is None:
        return default
    try:
        return element.text.strip()
    except (StaleElementReferenceException, WebDriverException):
        return default

def close_popups(driver: WebDriver, selectors: List[str]) -> None:
    for selector in selectors:
        try:
            close_btn = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            close_btn.click()
            logger.info("Closed popup using selector: %s", selector)
            return
        except (TimeoutException, NoSuchElementException):
            continue
        except WebDriverException as exc:
            logger.debug("Popup close attempt failed: %s", exc)
            continue
    logger.debug("No popup detected (this is normal).")

def scroll_to_bottom(driver: WebDriver, pause: float = 0.5, steps: int = 4) -> None:
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(1, steps + 1):
        target = int(last_height * (i / steps))
        driver.execute_script(f"window.scrollTo(0, {target});")
        time.sleep(pause)

def scroll_into_view(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
        element,
    )
    time.sleep(0.3)


# --- Review Parsing (from scraper/parser.py) ---

def _extract_rating(card: WebElement) -> Optional[int]:
    element = find_first(card, REVIEW_RATING_SELECTORS)
    raw_text = safe_text(element)
    if not raw_text:
        try:
            candidates = card.find_elements(By.XPATH, ".//div | .//span | .//p")
        except NoSuchElementException:
            candidates = []
        for candidate in candidates:
            text = safe_text(candidate).strip()
            if text and len(text) <= 3 and re.fullmatch(r"[1-5](\.\d)?★?", text):
                raw_text = text
                break
    if not raw_text:
        return None
    match = re.search(r"\d+", raw_text)
    if not match:
        return None
    try:
        rating = int(match.group())
        if 1 <= rating <= 5:
            return rating
    except ValueError:
        pass
    return None

def _extract_verified(card: WebElement) -> bool:
    element = find_first(card, VERIFIED_PURCHASE_SELECTORS)
    text = safe_text(element).lower()
    if "verified purchase" in text or "certified buyer" in text:
        return True
    full_text = safe_text(card).lower()
    return "verified purchase" in full_text or "certified buyer" in full_text

def _extract_title_and_body(card: WebElement) -> tuple[str, str]:
    title = safe_text(find_first(card, REVIEW_TITLE_SELECTORS))
    body = safe_text(find_first(card, REVIEW_TEXT_SELECTORS))
    if body or title:
        return title, body
    raw_text = safe_text(card)
    if not raw_text:
        return title, body
    boilerplate_markers = (
        "verified purchase",
        "certified buyer",
        "helpful",
        "report abuse",
        "read more",
        "permalink",
    )
    lines = [
        line.strip()
        for line in raw_text.split("\n")
        if line.strip() and not any(marker in line.strip().lower() for marker in boilerplate_markers)
    ]
    text_lines = [line for line in lines if len(line) > 3 and not line.replace(".", "").isdigit()]
    if not text_lines:
        return title, body
    if not title and len(text_lines) >= 1:
        title = text_lines[0]
    if not body:
        body_lines = text_lines[1:] if len(text_lines) > 1 else text_lines
        body = " ".join(body_lines).strip()
    return title, body

def parse_review_card(
    card: WebElement, product_name: str, product_url: str
) -> Optional[Review]:
    title, body = _extract_title_and_body(card)
    if not body and not title:
        logger.debug("Skipping card with no extractable title/body text.")
        return None
    rating = _extract_rating(card)
    date_text = safe_text(find_first(card, REVIEW_DATE_SELECTORS))
    reviewer_name = safe_text(find_first(card, REVIEWER_NAME_SELECTORS), default="Anonymous")
    verified = _extract_verified(card)
    return Review(
        product_name=product_name,
        review_title=title,
        review_text=body,
        rating=rating,
        review_date_raw=date_text,
        reviewer_name=reviewer_name or "Anonymous",
        verified_purchase=verified,
        product_url=product_url,
    )


# --- Data Cleaning (from preprocessing/clean_reviews.py) ---

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
MULTI_SPACE_PATTERN = re.compile(r"\s+")
BOILERPLATE_MARKERS = [
    "ABOUT Contact Us",
    "CIN :",
    "Hang on, loading content",
    "Registered Office Address",
    "GROUP COMPANIES",
    "Become a Seller",
]
MIN_REVIEW_TEXT_LEN = 3
MAX_REVIEW_TEXT_LEN = 2000
DATE_STUB_PATTERN = re.compile(
    r"^[,·\s]*[A-Za-z0-9.,\s]*"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s*\d{4}\s*$",
    re.IGNORECASE,
)

def _strip_html(text: str) -> str:
    return HTML_TAG_PATTERN.sub(" ", text)

def _normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)

def _remove_emojis(text: str) -> str:
    return "".join(c for c in text if unicodedata.category(c) != "So")

def _clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = _strip_html(text)
    text = _normalize_unicode(text)
    text = _remove_emojis(text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = MULTI_SPACE_PATTERN.sub(" ", text)
    return text.strip()

def _parse_review_date(raw: str) -> pd.Timestamp:
    if pd.isna(raw) or not str(raw).strip():
        return pd.NaT
    cleaned = str(raw).replace("Reviewed on", "").strip()
    parsed = pd.to_datetime(cleaned, errors="coerce", dayfirst=True)
    return parsed

def _is_boilerplate(text: str) -> bool:
    if len(text) > MAX_REVIEW_TEXT_LEN:
        return True
    return any(marker.lower() in text.lower() for marker in BOILERPLATE_MARKERS)

def _is_junk_fragment(text: str) -> bool:
    if len(text) < MIN_REVIEW_TEXT_LEN:
        return True
    if DATE_STUB_PATTERN.match(text):
        return True
    return False

def reviews_to_raw_dataframe(reviews: List[Review]) -> pd.DataFrame:
    records = [r.to_dict() for r in reviews]
    df = pd.DataFrame.from_records(records)
    logger.info("Built raw DataFrame with %d rows", len(df))
    return df

def clean_reviews(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        logger.warning("Raw DataFrame is empty - nothing to clean.")
        return df_raw.copy()
    df = df_raw.copy()
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    initial_count = len(df)
    text_columns = ["review_title", "review_text", "reviewer_name", "product_name"]
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(_clean_text)
    df = df[(df["review_text"].str.len() > 0) | (df["review_title"].str.len() > 0)]
    df = df.dropna(subset=["product_name", "product_url"])
    df = df[df["product_name"].str.len() > 0]
    before_boilerplate = len(df)
    df = df[~df["review_text"].apply(_is_boilerplate)]
    boilerplate_removed = before_boilerplate - len(df)
    if boilerplate_removed:
        logger.info("Removed %d boilerplate/page-wrapper rows", boilerplate_removed)
    before_junk = len(df)
    df = df[~df["review_text"].apply(_is_junk_fragment)]
    junk_removed = before_junk - len(df)
    if junk_removed:
        logger.info("Removed %d junk/fragment rows", junk_removed)
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")
    if "review_date_raw" in df.columns:
        df["review_date"] = df["review_date_raw"].apply(_parse_review_date)
    if "scraped_at" in df.columns:
        df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")
    if "reviewer_name" in df.columns:
        df["reviewer_name"] = df["reviewer_name"].replace("", "Anonymous").fillna("Anonymous")
    if "verified_purchase" in df.columns:
        df["verified_purchase"] = df["verified_purchase"].fillna(False).astype(bool)
    def calculate_row_hash(row) -> str:
        text = str(row.get("review_text", "")).strip().lower()
        date_raw = str(row.get("review_date_raw", "")).strip().lower()
        product = str(row.get("product_name", "")).strip().lower()
        key = f"{text}|{date_raw}|{product}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()
    df["content_hash"] = df.apply(calculate_row_hash, axis=1)
    df = df.drop_duplicates(subset=["content_hash"], keep="first")
    df = df.reset_index(drop=True)
    removed = initial_count - len(df)
    logger.info(
        "Cleaning complete: %d -> %d rows (%d removed as duplicate/invalid/empty/boilerplate)",
        initial_count,
        len(df),
        removed,
    )
    return df


# --- MongoDB Manager (from database/mongo.py) ---

class MongoManager:
    def __init__(self) -> None:
        if not MONGODB_URI:
            raise ValueError(
                "MONGODB_URI is not set. Please add it to your .env file "
                "(see .env.example)."
            )
        logger.info("Connecting to MongoDB Atlas (db='%s')", MONGO_DB_NAME)
        self.client: MongoClient = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
        try:
            self.client.admin.command("ping")
            logger.info("MongoDB connection successful")
        except ConnectionFailure as exc:
            logger.error("Failed to connect to MongoDB Atlas: %s", exc)
            raise
        self.db = self.client[MONGO_DB_NAME]
        self.collection: Collection = self.db[MONGO_COLLECTION_NAME]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.collection.create_index(
            [("content_hash", ASCENDING)], unique=True, name="uniq_content_hash"
        )
        logger.info("Ensured unique index on 'content_hash'")

    def insert_reviews_df(self, df: pd.DataFrame) -> int:
        if df.empty:
            logger.warning("No reviews to insert - DataFrame is empty.")
            return 0
        documents: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            doc = row.to_dict()
            review = Review(
                product_name=str(doc.get("product_name", "")),
                review_title=str(doc.get("review_title", "")),
                review_text=str(doc.get("review_text", "")),
                rating=None if pd.isna(doc.get("rating")) else int(doc.get("rating")),
                review_date_raw=str(doc.get("review_date_raw", "")),
                reviewer_name=str(doc.get("reviewer_name", "")),
                verified_purchase=bool(doc.get("verified_purchase", False)),
                product_url=str(doc.get("product_url", "")),
            )
            doc["content_hash"] = review.content_hash()
            for key, value in doc.items():
                if isinstance(value, pd.Timestamp):
                    doc[key] = value.isoformat() if not pd.isna(value) else None
                elif pd.isna(value) if not isinstance(value, (list, dict)) else False:
                    doc[key] = None
            documents.append(doc)
        try:
            result = self.collection.insert_many(documents, ordered=False)
            inserted_count = len(result.inserted_ids)
        except BulkWriteError as bwe:
            write_errors = bwe.details.get("writeErrors", [])
            duplicate_errors = [e for e in write_errors if e.get("code") == 11000]
            other_errors = [e for e in write_errors if e.get("code") != 11000]
            attempted = len(documents)
            failed = len(write_errors)
            inserted_count = attempted - failed
            logger.info(
                "Insert finished with %d duplicates skipped.", len(duplicate_errors)
            )
            if other_errors:
                logger.error("Encountered %d non-duplicate write errors: %s", len(other_errors), other_errors[:3])
        except PyMongoError as exc:
            logger.error("MongoDB insertion failed: %s", exc)
            raise
        logger.info("Inserted %d new review documents into MongoDB", inserted_count)
        return inserted_count

    def test_connection(self) -> bool:
        try:
            self.client.admin.command("ping")
            logger.info("MongoDB connection verification: SUCCESS")
            return True
        except Exception as exc:
            logger.error("MongoDB connection verification: FAILED - %s", exc)
            return False

    def close(self) -> None:
        self.client.close()
        logger.info("MongoDB connection closed.")


# --- Flipkart Scraper (from scraper/flipkart_scraper.py) ---

class FlipkartReviewScraper:
    def __init__(self, driver: Optional[WebDriver] = None) -> None:
        self.driver: WebDriver = driver or build_driver()
        self.wait = WebDriverWait(self.driver, EXPLICIT_WAIT_TIMEOUT)
        self.product_name: str = ""
        self.product_url: str = ""

    def scrape(self, search_query: str) -> List[Review]:
        logger.info("Starting scrape for query: '%s'", search_query)
        self._open_homepage()
        self._search_product(search_query)
        self._open_first_product()
        self._navigate_to_reviews()
        reviews = self._collect_all_reviews()
        logger.info(
            "Finished scraping '%s'. Total reviews collected: %d",
            self.product_name or search_query,
            len(reviews),
        )
        return reviews

    def close(self) -> None:
        try:
            self.driver.quit()
            logger.info("WebDriver session closed.")
        except Exception as exc:
            logger.warning("Error while closing WebDriver: %s", exc)

    def _open_homepage(self) -> None:
        logger.info("Opening Flipkart homepage")
        self.driver.get(FLIPKART_BASE_URL)
        close_popups(self.driver, LOGIN_POPUP_CLOSE_SELECTORS)

    @retry_on_exception(exceptions=(TimeoutException, StaleElementReferenceException))
    def _search_product(self, query: str) -> None:
        logger.info("Searching for product: '%s'", query)
        search_box = wait_for_any(self.driver, SEARCH_BOX_SELECTORS)
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)
        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        close_popups(self.driver, GENERIC_CLOSE_BUTTON_SELECTORS)

    @retry_on_exception(exceptions=(TimeoutException, StaleElementReferenceException))
    def _open_first_product(self) -> None:
        logger.info("Opening first product result")
        scroll_to_bottom(self.driver, pause=0.3, steps=2)
        first_product = wait_for_any(self.driver, FIRST_PRODUCT_SELECTORS)
        scroll_into_view(self.driver, first_product)
        try:
            first_product.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", first_product)
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        close_popups(self.driver, GENERIC_CLOSE_BUTTON_SELECTORS)
        self.product_url = self.driver.current_url
        self.product_name = self._extract_product_name()
        logger.info("Product opened: '%s' (%s)", self.product_name, self.product_url)

    def _extract_product_name(self) -> str:
        title_selectors = ["span.VU-ZEz", "span.B_NuCI", "h1 span", "span._35Ky9a"]
        element = find_first(self.driver, title_selectors)
        if element is not None:
            text = element.text.strip()
            if text:
                return text
        title = self.driver.title.strip()
        return title.split("|")[0].strip() if title else "Unknown Product"

    @retry_on_exception(exceptions=(TimeoutException, StaleElementReferenceException))
    def _navigate_to_reviews(self) -> None:
        logger.info("Navigating to Ratings & Reviews section")
        review_url = self.product_url.replace("/p/", "/product-reviews/")
        logger.info("Direct review URL: %s", review_url)
        self.driver.get(review_url)
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[contains(text(), 'Verified Purchase') or "
                        "contains(text(), 'Certified Buyer')]",
                    )
                )
            )
        except TimeoutException:
            logger.warning(
                "Review content did not appear within wait timeout; "
                "proceeding anyway (product may genuinely have 0 reviews, "
                "or content is blocked/slow to load)."
            )
        close_popups(self.driver, GENERIC_CLOSE_BUTTON_SELECTORS)
        logger.info("Reviews page opened: %s", self.driver.current_url)

    def _dump_no_cards_debug(self) -> None:
        try:
            os.makedirs("logs", exist_ok=True)
            self.driver.save_screenshot("logs/no_cards_debug.png")
            with open("logs/no_cards_debug.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.error(
                "No review cards matched any selector. Saved "
                "logs/no_cards_debug.png and logs/no_cards_debug.html "
                "for inspection."
            )
        except Exception as exc:
            logger.debug("Could not save no-cards debug artifacts: %s", exc)

    def _collect_all_reviews(self) -> List[Review]:
        all_reviews: List[Review] = []
        seen_review_keys = set()
        page_number = 1
        base_reviews_url = self.driver.current_url.replace("/p/", "/product-reviews/")
        if "?" in base_reviews_url:
            base_reviews_url = base_reviews_url.split("?")[0]
        import urllib.parse as urlparse
        parsed_url = urlparse.urlparse(self.product_url)
        params = urlparse.parse_qs(parsed_url.query)
        pid = params.get("pid", [""])[0]
        lid = params.get("lid", [""])[0]
        logger.info("Starting collection using URL-based pagination. Base: %s", base_reviews_url)
        progress = tqdm(desc="Scraping reviews", unit=" reviews")
        REVIEW_LIMIT = 500
        while page_number <= MAX_REVIEW_PAGES:
            if len(all_reviews) >= REVIEW_LIMIT:
                logger.info("Reached the review limit of %d. Stopping.", REVIEW_LIMIT)
                break
            paginated_url = f"{base_reviews_url}?pid={pid}&lid={lid}&marketplace=FLIPKART&page={page_number}"
            logger.info("Processing review page %d: %s", page_number, paginated_url)
            self.driver.get(paginated_url)
            time.sleep(2)
            scroll_to_bottom(self.driver, pause=0.5, steps=3)
            cards = self._find_review_cards()
            if not cards:
                logger.warning("No cards found on page %d. Retrying...", page_number)
                time.sleep(3)
                cards = self._find_review_cards()
                if not cards:
                    logger.info("No more reviews found. Ending collection.")
                    break
            page_reviews_count = 0
            for card in cards:
                if len(all_reviews) >= REVIEW_LIMIT:
                    break
                try:
                    review = parse_review_card(card, self.product_name, self.product_url)
                except Exception:
                    continue
                if review is not None:
                    review_key = f"{review.review_text.strip().lower()}|{review.review_date_raw.strip().lower()}"
                    if review_key not in seen_review_keys:
                        seen_review_keys.add(review_key)
                        all_reviews.append(review)
                        page_reviews_count += 1
                        progress.update(1)
            logger.info("Page %d: collected %d unique reviews (Total: %d)", page_number, page_reviews_count, len(all_reviews))
            if page_reviews_count == 0:
                logger.info("No new unique reviews found on page %d. Likely reached end of reviews.", page_number)
                break
            page_number += 1
        progress.close()
        return all_reviews

    @retry_on_exception(exceptions=(StaleElementReferenceException,))
    def _find_review_cards(self):
        for selector in REVIEW_CARD_SELECTORS:
            cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                return cards
        markers = self.driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Verified Purchase') or "
            "contains(text(), 'Certified Buyer')]",
        )
        if not markers:
            return []
        logger.warning(
            "Used structural XPath fallback for review cards "
            "(configured CSS selectors are stale)."
        )
        cards = []
        seen_texts = set()
        for marker in markers:
            try:
                current = marker
                chosen = None
                for _ in range(4):
                    try:
                        parent = current.find_element(By.XPATH, "..")
                    except Exception:
                        break
                    if parent.tag_name.lower() in ("body", "html"):
                        break
                    try:
                        parent_text = parent.text.lower()
                    except Exception:
                        break
                    marker_count = parent_text.count("certified buyer") + parent_text.count("verified purchase")
                    if marker_count > 1:
                        chosen = current
                        break
                    else:
                        chosen = parent
                    current = parent
                if chosen is None or chosen.tag_name.lower() != "div":
                    continue
                text = chosen.text.strip()
                if len(text) < 30:
                    continue
                if text in seen_texts:
                    continue
                seen_texts.add(text)
                cards.append(chosen)
            except Exception as exc:
                logger.debug("Error processing marker for structural fallback: %s", exc)
                continue
        return cards


# --- Main execution logic (from main.py) ---

def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "product"

def run_pipeline(search_query: str) -> None:
    try:
        mongo = MongoManager()
        if not mongo.test_connection():
            logger.warning("MongoDB connection check failed. Pipeline will continue but database insertion may fail.")
        mongo.close()
    except Exception as exc:
        logger.warning("Initial MongoDB connection check failed: %s. Pipeline will continue but database insertion may fail.", exc)

    start_time = time.time()
    slug = slugify(search_query)

    print(f"\n>>> Search Product: {search_query}")
    logger.info("=" * 70)
    logger.info("PIPELINE START - query='%s'", search_query)

    scraper = FlipkartReviewScraper()
    try:
        reviews = scraper.scrape(search_query)
    finally:
        scraper.close()

    if not reviews:
        logger.error("No reviews were collected. Aborting pipeline for '%s'.", search_query)
        print("\nNo reviews found for this product. Please try a different search term.")
        return

    print(f"\n>>> Product Found: {scraper.product_name}")
    print(f">>> Reviews Collected: {len(reviews)}")

    df_raw = reviews_to_raw_dataframe(reviews)
    raw_path = RAW_DATA_DIR / f"{slug}_reviews_raw.csv"
    df_raw.to_csv(raw_path, index=False, encoding="utf-8-sig")
    logger.info("Saved raw CSV: %s (%d rows)", raw_path, len(df_raw))
    print(f">>> Saved Raw CSV: {raw_path} ({len(df_raw)} rows)")

    df_clean = clean_reviews(df_raw)
    processed_path = PROCESSED_DATA_DIR / f"{slug}_reviews_clean.csv"
    df_clean.to_csv(processed_path, index=False, encoding="utf-8-sig")
    logger.info("Saved processed CSV: %s (%d rows)", processed_path, len(df_clean))
    print(f">>> Saved Clean CSV: {processed_path} ({len(df_clean)} rows)")

    try:
        mongo = MongoManager()
        inserted = mongo.insert_reviews_df(df_clean)
        mongo.close()
        print(f">>> Mongo Insert Count: {inserted}")
    except Exception as exc:
        logger.error("MongoDB step failed: %s", exc)
        print(
            f">>> Mongo Insert Count: 0 (FAILED - check MONGODB_URI in .env. Error: {exc})"
        )

    elapsed = time.time() - start_time
    logger.info("PIPELINE FINISHED in %.2f seconds", elapsed)
    print(f"\n>>> Finished in {elapsed:.2f} seconds.\n")

def main() -> None:
    print("=" * 70)
    print(" Flipkart Review Scraper - Data Pipeline (Subgroup 1)")
    print("=" * 70)

    try:
        search_query = input("\nSearch Product: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nNo input received. Exiting.")
        sys.exit(0)

    if not search_query:
        print("No product entered. Exiting.")
        sys.exit(1)

    try:
        run_pipeline(search_query)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user (Ctrl+C).")
        print("\nInterrupted by user. Exiting.")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unhandled error in pipeline: %s", exc)
        print(f"\nAn unexpected error occurred: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
