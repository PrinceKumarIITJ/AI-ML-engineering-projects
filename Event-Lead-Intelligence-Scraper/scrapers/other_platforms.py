"""
Scrapers for WedMeGood, WeddingWire, JustDial, and IndiaMART.
Each scraper uses Playwright to navigate the platform and extract business listings.
"""
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper
import re
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# WedMeGood Scraper
# ─────────────────────────────────────────────────────────────────────
class WedMeGoodScraper(BaseScraper):
    """
    Scrapes https://www.wedmegood.com/vendors/all/wedding-planners/<city>/
    WedMeGood has clean listing pages with pagination.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "WedMeGood"

    def _build_url(self, city: str, page_num: int = 1) -> str:
        city_slug = city.lower().replace(" ", "-")
        # WedMeGood URL pattern
        base = f"https://www.wedmegood.com/vendors/all/wedding-planners/{city_slug}/"
        if page_num > 1:
            base += f"?page={page_num}"
        return base

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        self.start_browser()
        page = self.get_new_page()
        results = []

        try:
            page_num = 1
            max_pages = max(limit // 15, 10)  # ~15 results per page

            while len(results) < limit and page_num <= max_pages:
                url = self._build_url(city, page_num)
                logger.info(f"[{self.platform_name}] Page {page_num}: {url}")

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay(2.0, 4.0)
                except Exception as e:
                    logger.warning(f"[{self.platform_name}] Page load failed: {e}")
                    break

                # Extract vendor cards
                cards = page.query_selector_all('div.vendor-card, div.vendor_card, div[class*="vendorCard"], a[class*="vendor-tile"]')
                if not cards:
                    # Try alternative selectors
                    cards = page.query_selector_all('div.vendor-list-item, div[class*="VendorCard"]')

                if not cards:
                    logger.info(f"[{self.platform_name}] No cards on page {page_num}, ending.")
                    break

                for card in cards:
                    try:
                        biz = self._parse_card(card, page, city)
                        if biz and biz.get('business_name') and biz['business_name'] != 'Unknown':
                            results.append(biz)
                    except Exception as e:
                        logger.debug(f"Card parse error: {e}")

                page_num += 1

                if len(results) >= limit:
                    break

        except Exception as e:
            logger.error(f"[{self.platform_name}] Scrape error: {e}")
        finally:
            self.stop_browser()

        logger.info(f"[{self.platform_name}] Collected {len(results)} for {city}")
        return results

    def _parse_card(self, card, page, city: str) -> Optional[Dict[str, Any]]:
        data = {
            "business_name": "Unknown",
            "city": city,
            "state": GoogleMapsScraper._get_state(city),
            "category": "Wedding Planner",
            "source_platforms": [self.platform_name],
            "source_urls": [],
            "services_offered": ["Wedding Planning"],
            "rating": None,
            "review_count": None,
            "contact_number": None,
            "full_address": None,
            "website": None,
            "price_range": None,
        }

        # Name
        name_el = card.query_selector('h3, h2, a[class*="vendor-name"], div[class*="name"], span[class*="name"]')
        if name_el:
            data['business_name'] = name_el.inner_text().strip()

        # Link
        link_el = card.query_selector('a[href]')
        if link_el:
            href = link_el.get_attribute('href') or ""
            if href and not href.startswith('http'):
                href = f"https://www.wedmegood.com{href}"
            data['source_urls'] = [href]

        # Rating
        rating_el = card.query_selector('span[class*="rating"], div[class*="rating"]')
        if rating_el:
            text = rating_el.inner_text().strip()
            try:
                data['rating'] = float(re.search(r'[\d.]+', text).group())
            except Exception:
                pass

        # Reviews
        review_el = card.query_selector('span[class*="review"], div[class*="review"]')
        if review_el:
            text = review_el.inner_text().strip()
            try:
                data['review_count'] = int(re.sub(r'\D', '', text))
            except Exception:
                pass

        # Price
        price_el = card.query_selector('span[class*="price"], div[class*="price"]')
        if price_el:
            data['price_range'] = price_el.inner_text().strip()

        # Location detail
        loc_el = card.query_selector('span[class*="location"], div[class*="location"], span[class*="city"]')
        if loc_el:
            data['full_address'] = loc_el.inner_text().strip()

        return data


# ─────────────────────────────────────────────────────────────────────
# WeddingWire India Scraper
# ─────────────────────────────────────────────────────────────────────
class WeddingWireScraper(BaseScraper):
    """
    Scrapes https://www.weddingwire.in/wedding-planners/<city>
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "WeddingWire India"

    def _build_url(self, city: str, page_num: int = 1) -> str:
        city_slug = city.lower().replace(" ", "-")
        base = f"https://www.weddingwire.in/wedding-planners/{city_slug}"
        if page_num > 1:
            base += f"--pn-{page_num}"
        return base

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        self.start_browser()
        page = self.get_new_page()
        results = []

        try:
            page_num = 1
            max_pages = max(limit // 15, 10)

            while len(results) < limit and page_num <= max_pages:
                url = self._build_url(city, page_num)
                logger.info(f"[{self.platform_name}] Page {page_num}: {url}")

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay(2.0, 4.0)
                except Exception as e:
                    logger.warning(f"[{self.platform_name}] Page load failed: {e}")
                    break

                # Vendor cards
                cards = page.query_selector_all('div.app-search-card, div[class*="StoreFrontCard"], div[class*="vendor-card"]')
                if not cards:
                    cards = page.query_selector_all('article, div.storefronts-card')

                if not cards:
                    logger.info(f"[{self.platform_name}] No cards on page {page_num}")
                    break

                for card in cards:
                    try:
                        biz = self._parse_card(card, city)
                        if biz and biz.get('business_name') and biz['business_name'] != 'Unknown':
                            results.append(biz)
                    except Exception as e:
                        logger.debug(f"Card parse error: {e}")

                page_num += 1

        except Exception as e:
            logger.error(f"[{self.platform_name}] Error: {e}")
        finally:
            self.stop_browser()

        logger.info(f"[{self.platform_name}] Collected {len(results)} for {city}")
        return results

    def _parse_card(self, card, city: str) -> Optional[Dict[str, Any]]:
        data = {
            "business_name": "Unknown",
            "city": city,
            "state": GoogleMapsScraper._get_state(city),
            "category": "Wedding Planner",
            "source_platforms": [self.platform_name],
            "source_urls": [],
            "services_offered": ["Wedding Planning"],
            "rating": None,
            "review_count": None,
            "price_range": None,
            "full_address": None,
        }

        # Name
        name_el = card.query_selector('a.app-search-card__title, h2, h3, a[class*="title"], span[class*="name"]')
        if name_el:
            data['business_name'] = name_el.inner_text().strip()
            href = name_el.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = f"https://www.weddingwire.in{href}"
                data['source_urls'] = [href]

        # Rating
        rating_el = card.query_selector('span[class*="rating"], div[class*="rating-score"]')
        if rating_el:
            try:
                data['rating'] = float(re.search(r'[\d.]+', rating_el.inner_text()).group())
            except Exception:
                pass

        # Reviews
        review_el = card.query_selector('span[class*="review"], a[class*="review"]')
        if review_el:
            try:
                data['review_count'] = int(re.sub(r'\D', '', review_el.inner_text()))
            except Exception:
                pass

        # Price
        price_el = card.query_selector('span[class*="price"], div[class*="price"]')
        if price_el:
            data['price_range'] = price_el.inner_text().strip()

        # Location
        loc_el = card.query_selector('span[class*="location"], a[class*="location"]')
        if loc_el:
            data['full_address'] = loc_el.inner_text().strip()

        return data


# ─────────────────────────────────────────────────────────────────────
# JustDial Scraper
# ─────────────────────────────────────────────────────────────────────
class JustDialScraper(BaseScraper):
    """
    Scrapes JustDial listings. JustDial encodes phone numbers in a custom font,
    so we focus on extracting name, address, rating, and category.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "JustDial"

    def _build_url(self, keyword: str, city: str, page_num: int = 1) -> str:
        city_slug = city.lower().replace(" ", "-")
        keyword_slug = keyword.lower().replace(" ", "-")
        base = f"https://www.justdial.com/{city_slug}/{keyword_slug}"
        if page_num > 1:
            base += f"/page-{page_num}"
        return base

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        self.start_browser()
        page = self.get_new_page()
        results = []

        try:
            page_num = 1
            max_pages = max(limit // 20, 8)

            while len(results) < limit and page_num <= max_pages:
                url = self._build_url(keyword, city, page_num)
                logger.info(f"[{self.platform_name}] Page {page_num}: {url}")

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay(3.0, 5.0)
                except Exception as e:
                    logger.warning(f"[{self.platform_name}] Page load failed: {e}")
                    break

                # Handle CAPTCHA popup if present — just close it
                try:
                    close_btn = page.query_selector('span.jdicon-close, button[class*="close"]')
                    if close_btn:
                        close_btn.click()
                        self.random_delay(1.0, 2.0)
                except Exception:
                    pass

                # Scroll to trigger lazy loading
                self.human_scroll(page, 5)

                # Extract listing cards
                cards = page.query_selector_all('li.cntanr, div[class*="resultbox"], div.store-details, li[class*="cntanr"]')
                if not cards:
                    # Updated selectors for newer JD layout
                    cards = page.query_selector_all('div[class*="resultbox_info"], div[class*="jsx-"]')

                if not cards:
                    logger.info(f"[{self.platform_name}] No cards on page {page_num}")
                    break

                for card in cards:
                    try:
                        biz = self._parse_card(card, city)
                        if biz and biz.get('business_name') and biz['business_name'] != 'Unknown':
                            results.append(biz)
                    except Exception as e:
                        logger.debug(f"Card parse error: {e}")

                page_num += 1

        except Exception as e:
            logger.error(f"[{self.platform_name}] Error: {e}")
        finally:
            self.stop_browser()

        logger.info(f"[{self.platform_name}] Collected {len(results)} for {city}")
        return results

    def _parse_card(self, card, city: str) -> Optional[Dict[str, Any]]:
        data = {
            "business_name": "Unknown",
            "city": city,
            "state": GoogleMapsScraper._get_state(city),
            "category": "Event Management",
            "source_platforms": [self.platform_name],
            "source_urls": [],
            "services_offered": [],
            "rating": None,
            "review_count": None,
            "full_address": None,
            "contact_number": None,
        }

        # Name
        name_el = card.query_selector('span.lng_cont_name, a.lng_cont_name, h2, h3, a[class*="title"], span[class*="store-name"]')
        if name_el:
            data['business_name'] = name_el.inner_text().strip()
            href = name_el.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = f"https://www.justdial.com{href}"
                data['source_urls'] = [href]

        # Rating
        rating_el = card.query_selector('span.green-box, span[class*="rating"], span[class*="star"]')
        if rating_el:
            try:
                data['rating'] = float(re.search(r'[\d.]+', rating_el.inner_text()).group())
            except Exception:
                pass

        # Reviews / Votes
        review_el = card.query_selector('span.rt_count, span[class*="votes"], span[class*="review"]')
        if review_el:
            try:
                data['review_count'] = int(re.sub(r'\D', '', review_el.inner_text()))
            except Exception:
                pass

        # Address
        addr_el = card.query_selector('span.cont_fl_addr, span[class*="address"], p[class*="address"]')
        if addr_el:
            data['full_address'] = addr_el.inner_text().strip()
            pin_match = re.search(r'\b(\d{6})\b', data['full_address'])
            if pin_match:
                data['pincode'] = pin_match.group(1)

        # Category tags
        cat_el = card.query_selector('span.lng_cont_cat, span[class*="category"]')
        if cat_el:
            cat_text = cat_el.inner_text().strip()
            data['category'] = cat_text
            data['services_offered'] = [s.strip() for s in cat_text.split(',')]

        # Phone - JustDial obfuscates phones with custom font, try to get from aria-label or data attribute
        phone_el = card.query_selector('a[href^="tel:"], span[class*="mobilesv"]')
        if phone_el:
            phone_text = phone_el.get_attribute('href') or phone_el.inner_text()
            phone_digits = re.sub(r'\D', '', phone_text)
            if len(phone_digits) >= 10:
                data['contact_number'] = phone_digits[-10:]

        return data


# ─────────────────────────────────────────────────────────────────────
# IndiaMART Scraper
# ─────────────────────────────────────────────────────────────────────
class IndiaMartScraper(BaseScraper):
    """
    Scrapes IndiaMart service provider listings.
    URL: https://dir.indiamart.com/search.mp?ss=event+management&city=<city>
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "IndiaMART"

    def _build_url(self, keyword: str, city: str, page_num: int = 1) -> str:
        kw = keyword.replace(" ", "+")
        city_lower = city.lower()
        base = f"https://dir.indiamart.com/search.mp?ss={kw}&city={city_lower}"
        if page_num > 1:
            base += f"&page={page_num}"
        return base

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        self.start_browser()
        page = self.get_new_page()
        results = []

        try:
            page_num = 1
            max_pages = max(limit // 20, 8)

            while len(results) < limit and page_num <= max_pages:
                url = self._build_url(keyword, city, page_num)
                logger.info(f"[{self.platform_name}] Page {page_num}: {url}")

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay(2.0, 4.0)
                except Exception as e:
                    logger.warning(f"[{self.platform_name}] Page load failed: {e}")
                    break

                # Close any floating popups
                try:
                    close_btns = page.query_selector_all('button[class*="close"], span[class*="close"]')
                    for btn in close_btns[:2]:
                        btn.click()
                        self.random_delay(0.5, 1.0)
                except Exception:
                    pass

                # Scroll to load lazy content
                self.human_scroll(page, 4)

                # Extract listings
                cards = page.query_selector_all('div.lst, div[class*="cardwrap"], div[class*="flx-bx"]')
                if not cards:
                    cards = page.query_selector_all('div[class*="product-card"], div.prd-card')

                if not cards:
                    logger.info(f"[{self.platform_name}] No cards on page {page_num}")
                    break

                for card in cards:
                    try:
                        biz = self._parse_card(card, city)
                        if biz and biz.get('business_name') and biz['business_name'] != 'Unknown':
                            results.append(biz)
                    except Exception as e:
                        logger.debug(f"Card parse error: {e}")

                page_num += 1

        except Exception as e:
            logger.error(f"[{self.platform_name}] Error: {e}")
        finally:
            self.stop_browser()

        logger.info(f"[{self.platform_name}] Collected {len(results)} for {city}")
        return results

    def _parse_card(self, card, city: str) -> Optional[Dict[str, Any]]:
        data = {
            "business_name": "Unknown",
            "city": city,
            "state": GoogleMapsScraper._get_state(city),
            "category": "Event Management",
            "source_platforms": [self.platform_name],
            "source_urls": [],
            "services_offered": [],
            "full_address": None,
            "contact_number": None,
            "website": None,
        }

        # Company Name
        name_el = card.query_selector('a.lcname, a[class*="company-name"], h2 a, h3 a, span.company-name')
        if name_el:
            data['business_name'] = name_el.inner_text().strip()
            href = name_el.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = f"https://dir.indiamart.com{href}"
                data['source_urls'] = [href]

        # Address / Location
        addr_el = card.query_selector('span.clr1, span[class*="location"], p[class*="address"], span.cityNameSrp')
        if addr_el:
            data['full_address'] = addr_el.inner_text().strip()
            pin_match = re.search(r'\b(\d{6})\b', data['full_address'] or "")
            if pin_match:
                data['pincode'] = pin_match.group(1)

        # Phone
        phone_el = card.query_selector('span[class*="phn"], a[href^="tel:"], span.mob_no')
        if phone_el:
            phone_text = phone_el.get_attribute('href') or phone_el.inner_text()
            digits = re.sub(r'\D', '', phone_text or "")
            if len(digits) >= 10:
                data['contact_number'] = digits[-10:]

        # Product/Service
        svc_el = card.query_selector('p[class*="product-name"], a[class*="product"], span.prd-name')
        if svc_el:
            data['services_offered'] = [svc_el.inner_text().strip()]

        return data


# ─────────────────────────────────────────────────────────────────────
# Google Search Scraper (for supplemental discovery)
# ─────────────────────────────────────────────────────────────────────
class GoogleSearchScraper(BaseScraper):
    """
    Uses Google Search results pages to discover event management businesses
    from various listing pages, directories, and social media profiles.
    This supplements the platform-specific scrapers.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "Google Search"

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        self.start_browser()
        page = self.get_new_page()
        results = []

        queries = [
            f'{keyword} in {city} contact number',
            f'best {keyword} {city}',
            f'top {keyword} {city} list',
            f'site:facebook.com {keyword} {city}',
            f'site:instagram.com {keyword} {city}',
        ]

        try:
            for query in queries:
                if len(results) >= limit:
                    break

                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=50"
                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay(3.0, 5.0)

                    # Extract search result entries
                    result_divs = page.query_selector_all('div.g, div[data-sokoban-container]')
                    for div in result_divs:
                        try:
                            biz = self._parse_search_result(div, city)
                            if biz:
                                results.append(biz)
                        except Exception:
                            pass

                except Exception as e:
                    logger.debug(f"[{self.platform_name}] Query failed: {e}")
                    self.random_delay(5.0, 10.0)  # Back off on failure

        except Exception as e:
            logger.error(f"[{self.platform_name}] Error: {e}")
        finally:
            self.stop_browser()

        logger.info(f"[{self.platform_name}] Collected {len(results)} for {city}")
        return results

    def _parse_search_result(self, div, city: str) -> Optional[Dict[str, Any]]:
        """Parse a Google Search result div to extract business info."""
        link_el = div.query_selector('a[href]')
        title_el = div.query_selector('h3')

        if not link_el or not title_el:
            return None

        title = title_el.inner_text().strip()
        href = link_el.get_attribute('href') or ""

        # Skip irrelevant results (news, maps redirect, etc.)
        skip_domains = ['youtube.com', 'google.com', 'wikipedia.org', 'quora.com']
        if any(d in href for d in skip_domains):
            return None

        # Determine social links
        data = {
            "business_name": self._clean_title(title),
            "city": city,
            "state": GoogleMapsScraper._get_state(city),
            "category": "Event Management",
            "source_platforms": [self.platform_name],
            "source_urls": [href],
            "services_offered": [],
        }

        if 'instagram.com' in href:
            data['instagram_url'] = href
        elif 'facebook.com' in href:
            data['facebook_url'] = href
        elif 'linkedin.com' in href:
            data['linkedin_url'] = href
        else:
            data['website'] = href

        # Snippet for phone/email
        snippet_el = div.query_selector('span.st, div[data-sncf], div[class*="VwiC3b"]')
        if snippet_el:
            snippet = snippet_el.inner_text()
            # Phone
            phone_match = re.search(r'(?:\+91[\s-]?)?([6-9]\d{9})', snippet)
            if phone_match:
                data['contact_number'] = phone_match.group(0).strip()
            # Email
            email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', snippet)
            if email_match:
                data['email'] = email_match.group(0)

        if not data['business_name'] or len(data['business_name']) < 3:
            return None

        return data

    @staticmethod
    def _clean_title(title: str) -> str:
        """Remove common suffixes from search result titles."""
        for suffix in [' - Home', ' | Facebook', ' | LinkedIn', ' (@', ' - Instagram',
                       ' - WedMeGood', ' - WeddingWire', ' | JustDial', ' - IndiaMART',
                       ' - About', ' - Reviews', ' Reviews', ' - Home | Facebook']:
            if suffix in title:
                title = title.split(suffix)[0]
        return title.strip()


# Re-export GoogleMapsScraper's state helper for use by other scrapers
from .google_maps import GoogleMapsScraper


class TheWeddingCompanyScraper(BaseScraper):
    """
    Scrapes TheWeddingCompany directory.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_name = "TheWeddingCompany"

    def scrape(self, keyword: str, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        self.start_browser()
        page = self.get_new_page()
        results = []

        # TheWeddingCompany uses location-based search
        city_slug = city.lower().replace(" ", "-")
        url = f"https://www.theweddingcompany.in/vendors/{city_slug}/all"

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=40000)
            self.random_delay(3.0, 5.0)
            
            page_num = 1
            max_pages = max(limit // 15, 8)

            while len(results) < limit and page_num <= max_pages:
                cards = page.query_selector_all('div.vendor-card, div.list-item, div.vendor-listing, article')
                
                if not cards:
                    break

                for card in cards:
                    try:
                        name_el = card.query_selector('h3, h2, a.title, span.vendor-name')
                        if not name_el: continue
                        
                        business_name = name_el.inner_text().strip()
                        href = name_el.get_attribute('href') or ""
                        if href and not href.startswith('http'):
                            href = f"https://www.theweddingcompany.in{href}"

                        address_el = card.query_selector('span.location, p.address, div.vendor-location')
                        address = address_el.inner_text().strip() if address_el else None
                        
                        results.append({
                            "business_name": business_name,
                            "city": city,
                            "category": "Wedding Vendor",
                            "source_platforms": [self.platform_name],
                            "source_urls": [href],
                            "services_offered": ["Wedding Services"],
                            "full_address": address,
                            "contact_number": None,
                            "website": href
                        })
                    except Exception:
                        pass
                
                # Try next page
                try:
                    next_btn = page.query_selector('a.next, a[rel="next"]')
                    if next_btn:
                        next_btn.click()
                        self.random_delay(2.0, 4.0)
                        page_num += 1
                    else:
                        break
                except Exception:
                    break
                    
        except Exception as e:
            logger.debug(f"[{self.platform_name}] Error: {e}")
        finally:
            self.stop_browser()

        return results