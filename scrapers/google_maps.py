"""
The Google Maps Agent.
This script automatically opens Google Maps, types in a search query (like 
"Wedding Planners in Jaipur"), and scrolls down the list of results. 
For every business it finds, it clicks on it and extracts the name, address, 
phone number, and star rating.
"""
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import re
import logging

logger = logging.getLogger(__name__)


class GoogleMapsScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "Google Maps"

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scrapes Google Maps for businesses matching keyword in city.
        Returns list of raw dicts ready for normalization.
        """
        self.start_browser()
        page = self.get_new_page()
        results = []

        search_query = f"{keyword} in {city}"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self.random_delay(4.0, 6.0)

            # Accept cookies if prompted
            try:
                accept_btn = page.query_selector('button[aria-label="Accept all"]')
                if accept_btn:
                    accept_btn.click()
                    self.random_delay(1.0, 2.0)
            except Exception:
                pass

            # Wait for the results feed
            try:
                page.wait_for_selector('div[role="feed"]', timeout=15000)
            except Exception:
                logger.warning(f"[{self.platform_name}] No results container for '{keyword}' in {city}")
                return results

            # Scroll the feed to load more results
            collected_hrefs = set()
            scroll_attempts = 0
            max_scrolls = max(limit // 3, 20)

            while len(collected_hrefs) < limit and scroll_attempts < max_scrolls:
                # Gather all listing links currently visible
                listings = page.query_selector_all('div[role="feed"] > div > div > a')
                for el in listings:
                    href = el.get_attribute('href')
                    if href and '/maps/place/' in href and href not in collected_hrefs:
                        collected_hrefs.add(href)

                # Scroll the feed panel
                feed = page.query_selector('div[role="feed"]')
                if feed:
                    feed.evaluate('(el) => el.scrollTop = el.scrollTop + 800')
                else:
                    page.mouse.wheel(0, 1500)

                self.random_delay(1.5, 3.0)
                scroll_attempts += 1

                # Check for "end of list"
                end_text = page.query_selector('p.fontBodyMedium > span > span')
                if end_text and "end of list" in (end_text.inner_text() or "").lower():
                    break

            logger.info(f"[{self.platform_name}] Found {len(collected_hrefs)} listings for '{keyword}' in {city}")

            # Now click each listing and extract details
            for idx, href in enumerate(list(collected_hrefs)[:limit]):
                try:
                    # Navigate directly to the place URL for reliability
                    page.goto(href, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay(2.0, 3.5)

                    business = self._parse_details_panel(page, city, href)
                    if business['business_name'] and business['business_name'] != "Unknown":
                        results.append(business)
                        if len(results) % 20 == 0:
                            logger.info(f"  [{self.platform_name}] Extracted {len(results)}/{len(collected_hrefs)} records...")

                except Exception as e:
                    logger.debug(f"Error parsing listing {idx}: {e}")

                if len(results) >= limit:
                    break

        except Exception as e:
            logger.error(f"[{self.platform_name}] Scrape error: {e}")

        finally:
            self.stop_browser()

        logger.info(f"[{self.platform_name}] Completed: {len(results)} records for '{keyword}' in {city}")
        return results

    def _parse_details_panel(self, page, city: str, url: str) -> Dict[str, Any]:
        """Parse the Google Maps place detail page."""
        data = {
            "business_name": "Unknown",
            "city": city,
            "state": self._get_state(city),
            "source_platforms": [self.platform_name],
            "source_urls": [url],
            "google_maps_url": url,
            "rating": None,
            "review_count": None,
            "full_address": None,
            "website": None,
            "contact_number": None,
            "category": "Event Management",
            "services_offered": [],
        }

        try:
            # Business Name
            title_el = page.query_selector('h1.DUwDvf')
            if not title_el:
                title_el = page.query_selector('h1')
            if title_el:
                data['business_name'] = title_el.inner_text().strip()

            # Category  
            cat_el = page.query_selector('button[jsaction="pane.rating.category"]')
            if cat_el:
                cat_text = cat_el.inner_text().strip()
                if cat_text:
                    data['category'] = cat_text
                    data['services_offered'].append(cat_text)

            # Rating & Reviews
            rating_el = page.query_selector('div.F7nice > span > span[aria-hidden="true"]')
            if rating_el:
                try:
                    data['rating'] = float(rating_el.inner_text().replace(",", ".").strip())
                except (ValueError, TypeError):
                    pass

            reviews_el = page.query_selector('div.F7nice > span:nth-child(2) > span > span')
            if reviews_el:
                try:
                    data['review_count'] = int(re.sub(r'\D', '', reviews_el.inner_text()))
                except (ValueError, TypeError):
                    pass

            # Info buttons (Address, Website, Phone)
            info_buttons = page.query_selector_all('button.CsEnBe')
            for btn in info_buttons:
                try:
                    aria = btn.get_attribute("aria-label") or ""
                    text = btn.inner_text().strip()

                    if "Address:" in aria or "address" in aria.lower():
                        data['full_address'] = text
                        # Try to extract pincode
                        pin_match = re.search(r'\b(\d{6})\b', text)
                        if pin_match:
                            data['pincode'] = pin_match.group(1)

                    elif "Website:" in aria or "website" in aria.lower():
                        data['website'] = text

                    elif "Phone:" in aria or "phone" in aria.lower():
                        phone_digits = re.sub(r'\D', '', text)
                        if len(phone_digits) >= 10:
                            data['contact_number'] = text

                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"Parse error: {e}")

        return data

    @staticmethod
    def _get_state(city: str) -> str:
        """Map target cities to their states."""
        state_map = {
            "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "udaipur": "Rajasthan",
            "delhi": "Delhi", "new delhi": "Delhi",
            "gurgaon": "Haryana", "gurugram": "Haryana",
            "noida": "Uttar Pradesh",
            "chandigarh": "Chandigarh",
            "indore": "Madhya Pradesh", "bhopal": "Madhya Pradesh",
        }
        return state_map.get(city.lower(), "Unknown")
