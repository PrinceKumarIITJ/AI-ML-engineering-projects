"""
The Discovery Agent (Enricher).
Sometimes we find a great business on Google Maps, but they don't list their 
email or Instagram. This script acts like a private investigator. 
It searches the broader internet (using DuckDuckGo) or visits the company's 
official website to "hunt" for missing contact information and social media links.
"""
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
    Finds missing data (like Instagram links or Phone numbers) 
    by automatically searching the web.
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

    def _extract_details_from_website(self, url: str) -> dict:
        """Fetches the official website HTML and looks for social media links and phone numbers."""
        if not url:
            return {}
            
        if not url.startswith('http'):
            url = f"http://{url}"
            
        response = self._safe_request(url)
        if not response:
            return {}
            
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = {}
            
            # 1. Socials
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                if 'instagram.com/' in href and 'instagram_url' not in results:
                    results['instagram_url'] = a['href']
                elif 'facebook.com/' in href and 'facebook_url' not in results:
                    results['facebook_url'] = a['href']
                elif 'linkedin.com/company/' in href and 'linkedin_url' not in results:
                    results['linkedin_url'] = a['href']
            
            # 2. Contact Numbers (Regex for Indian numbers)
            text_content = soup.get_text()
            phone_matches = re.findall(r'(?:\+91[\s-]?)?([6-9]\d{9})', text_content)
            if phone_matches:
                results['contact_number'] = phone_matches[0]
                if len(phone_matches) > 1:
                    results['alternate_number'] = phone_matches[1]

            return results
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
        
        # 1. Attempt to fetch details from known website
        if record.website and not (record.instagram_url and record.facebook_url and record.contact_number):
            found = self._extract_details_from_website(record.website)
            if 'instagram_url' in found and not record.instagram_url:
                record.instagram_url = found['instagram_url']
            if 'facebook_url' in found and not record.facebook_url:
                record.facebook_url = found['facebook_url']
            if 'linkedin_url' in found and not record.linkedin_url:
                record.linkedin_url = found['linkedin_url']
            if 'contact_number' in found and not record.contact_number:
                record.contact_number = found['contact_number']
            if 'alternate_number' in found and not record.alternate_number:
                record.alternate_number = found['alternate_number']

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
        from concurrent.futures import ThreadPoolExecutor
        
        total = len(records)
        logger.info(f"Starting parallel enrichment for {total} records...")
        
        # Use 10 threads for I/O bound enrichment
        with ThreadPoolExecutor(max_workers=10) as executor:
            enriched = list(executor.map(self.enrich_record, records))
            
        logger.info(f"Parallel enrichment complete for {total} records.")
        return enriched
