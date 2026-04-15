import time
import random
import logging
from typing import Optional, List, Dict, Any
from playwright.sync_api import sync_playwright, Page, BrowserContext
from config import USER_AGENTS

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all Playwright-based scrapers with anti-detection and stealth."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.platform_name = "Base"

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
        return self.context.new_page()

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
