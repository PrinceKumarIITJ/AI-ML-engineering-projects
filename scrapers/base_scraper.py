"""
The Stealth Engine (Base Scraper).
When our agent visits websites like JustDial, those websites try to block 
automated bots. This script is the "disguise". It tricks the websites into 
thinking our agent is a real human using a normal Google Chrome browser 
on a Windows computer.
"""
import time
import random
import logging
from typing import Optional, List, Dict, Any
from playwright.sync_api import sync_playwright, Page, BrowserContext
from playwright_stealth import Stealth

from config import USER_AGENTS

logger = logging.getLogger(__name__)


class BaseScraper:
    """
    The parent class for all our web scrapers. 
    It handles launching the browser, applying the stealth disguise, 
    and scrolling down the page just like a human would.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.platform_name = "Base"
        self.stealth_config = Stealth()


    def start_browser(self):
        """Launch Playwright Chromium with stealth settings."""
        self.playwright = sync_playwright().start()

        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-http2", # Key for JustDial/IndiaMART blocks
        ]

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=args
        )

        # Pick a random user agent
        user_agent = random.choice(USER_AGENTS)

        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
            locale='en-IN',
            timezone_id='Asia/Kolkata',
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Referer": "https://www.google.com/",
                "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Upgrade-Insecure-Requests": "1"
            }
        )

        # Stealth: override navigator.webdriver
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

    def stop_browser(self):
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        finally:
            self.context = None
            self.browser = None
            self.playwright = None

    def get_new_page(self) -> Page:
        if not self.context:
            self.start_browser()
        page = self.context.new_page()
        # Apply stealth to the specific page
        self.stealth_config.apply_stealth_sync(page)

        return page

    def random_delay(self, min_s: float = 1.0, max_s: float = 3.0):
        time.sleep(random.uniform(min_s, max_s))

    def human_scroll(self, page: Page, limit: int = 10):
        """Simulate human-like scrolling to trigger lazy loading."""
        for _ in range(limit):
            page.mouse.wheel(0, random.randint(300, 800))
            self.random_delay(0.5, 1.5)

    def safe_text(self, page: Page, selector: str) -> Optional[str]:
        """Safely extract inner text from a selector, returns None if not found."""
        try:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                return text if text else None
        except Exception:
            pass
        return None

    def safe_attr(self, page: Page, selector: str, attr: str) -> Optional[str]:
        """Safely extract an attribute from a selector."""
        try:
            el = page.query_selector(selector)
            if el:
                val = el.get_attribute(attr)
                return val.strip() if val else None
        except Exception:
            pass
        return None

    def scrape(self, keyword: str, city: str, limit: int = 50) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement scrape()")

    def close(self):
        self.stop_browser()
