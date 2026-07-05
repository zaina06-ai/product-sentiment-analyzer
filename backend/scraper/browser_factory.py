from __future__ import annotations

from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool
    page_load_timeout_seconds: int
    implicit_wait_seconds: int


def create_chrome_driver(*, config: BrowserConfig):
    options = Options()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        raise RuntimeError(
            "Failed to start Chrome WebDriver. Ensure chromedriver is installed and compatible with Chrome."
        ) from e

    driver.set_page_load_timeout(config.page_load_timeout_seconds)
    driver.implicitly_wait(config.implicit_wait_seconds)
    return driver

