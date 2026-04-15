import time
import requests
import random
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import quote_plus
from models.schema import BusinessSchema

logger = logging.getLogger(__name__)

class DataEnricher:
    """
    Enriches business records by searching for missing fields (social links, website)
    using public search engine queries (e.g., DuckDuckGo to avoid strict Google bans),
    or extracting from their verified website.
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        })

    def _safe_request(self, url: str) -> Optional[requests.Response]:
        try:
            time.sleep(random.uniform(1.0, 2.5))
            response = self.session.get(url, timeout=8)
            if response.status_code == 200:
                return response
        except Exception:
            pass
        return None

    def _extract_socials_from_website(self, url: str) -> dict:
        """Fetches the official website HTML and looks for social media links."""
        if not url:
            return {}
            
        if not url.startswith('http'):
            url = f"http://{url}"
            
        response = self._safe_request(url)
        if not response:
            return {}
            
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            socials = {}
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                if 'instagram.com/' in href and 'instagram_url' not in socials:
                    socials['instagram_url'] = a['href']
                elif 'facebook.com/' in href and 'facebook_url' not in socials:
                    socials['facebook_url'] = a['href']
                elif 'linkedin.com/company/' in href and 'linkedin_url' not in socials:
                    socials['linkedin_url'] = a['href']
            return socials
        except Exception:
            return {}

    def _search_engine_discovery(self, query: str) -> dict:
        """Uses DuckDuckGo HTML version to find the official website and socials if missing."""
        ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        res = self._safe_request(ddg_url)
        socials = {}
        website = None
        
        if res:
            try:
                soup = BeautifulSoup(res.text, 'html.parser')
                for a in soup.find_all('a', class_='result__url', href=True):
                    href = a.get('href', '').lower()
                    if 'http' not in href: 
                        continue
                    
                    if 'instagram.com/' in href and 'instagram_url' not in socials:
                        socials['instagram_url'] = href
                    elif 'facebook.com/' in href and 'facebook_url' not in socials:
                        socials['facebook_url'] = href
                    elif 'linkedin.com/company' in href and 'linkedin_url' not in socials:
                        socials['linkedin_url'] = href
                    elif not any(d in href for d in ['justdial', 'wedmegood', 'weddingwire', 'indiamart', 'sulekha', 'google']):
                        if not website:
                            website = href
            except Exception:
                pass
                        
        return {"website": website, **socials}

    def enrich_record(self, record: BusinessSchema) -> BusinessSchema:
        """Attempt to fill missing data without hallucination."""
        
        # 1. Attempt to fetch socials from known website
        if record.website and not (record.instagram_url and record.facebook_url):
            found = self._extract_socials_from_website(record.website)
            if 'instagram_url' in found and not record.instagram_url:
                record.instagram_url = found['instagram_url']
            if 'facebook_url' in found and not record.facebook_url:
                record.facebook_url = found['facebook_url']
            if 'linkedin_url' in found and not record.linkedin_url:
                record.linkedin_url = found['linkedin_url']

        # 2. Attempt search engine discovery if heavily missing
        elif not record.website and not record.instagram_url:
            query = f'"{record.business_name}" {record.city} event planner'
            found = self._search_engine_discovery(query)
            
            if 'website' in found and found['website'] and not record.website:
                record.website = found['website']
            if 'instagram_url' in found and found['instagram_url'] and not record.instagram_url:
                record.instagram_url = found['instagram_url']
            if 'facebook_url' in found and found['facebook_url'] and not record.facebook_url:
                record.facebook_url = found['facebook_url']

        return record

    def run_pipeline(self, records: List[BusinessSchema]) -> List[BusinessSchema]:
        enriched = []
        for i, r in enumerate(records):
            if i > 0 and i % 50 == 0:
                logger.info(f"Enriched {i}/{len(records)} records...")
            enriched.append(self.enrich_record(r))
        return enriched
