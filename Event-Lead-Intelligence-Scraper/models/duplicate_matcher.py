"""
Duplicate Matcher — weighted multi-field similarity scoring to detect
and cluster duplicate business records across different source platforms.
"""
from typing import List
from rapidfuzz import fuzz
from .schema import BusinessSchema
from config import DEDUPE_THRESHOLDS
import re
import logging

logger = logging.getLogger(__name__)


class DuplicateMatcher:
    def __init__(self):
        pass

    def clean_phone(self, phone: str) -> str:
        if not phone:
            return ""
        return re.sub(r'\D', '', phone)[-10:]  # Keep last 10 digits

    def clean_url(self, url: str) -> str:
        if not url:
            return ""
        return url.replace("https://", "").replace("http://", "").replace("www.", "").strip('/').lower()

    def calculate_similarity(self, b1: BusinessSchema, b2: BusinessSchema) -> float:
        """Calculates a weighted similarity score between two business records."""
        score = 0.0

        # 1. Name Similarity (Weight: 35%)
        if b1.business_name and b2.business_name:
            name_score = fuzz.token_sort_ratio(
                b1.business_name.lower(), b2.business_name.lower()
            ) / 100.0
            score += name_score * DEDUPE_THRESHOLDS["NAME_SIMILARITY"]

        # 2. Phone Exact Match (Weight: 25%)
        phones1 = {self.clean_phone(b1.contact_number), self.clean_phone(b1.alternate_number)} - {""}
        phones2 = {self.clean_phone(b2.contact_number), self.clean_phone(b2.alternate_number)} - {""}

        if phones1 and phones2 and phones1.intersection(phones2):
            score += DEDUPE_THRESHOLDS["PHONE_EXACT"]

        # 3. Website Exact Match (Weight: 15%)
        web1 = self.clean_url(b1.website)
        web2 = self.clean_url(b2.website)
        if web1 and web2 and web1 == web2:
            score += DEDUPE_THRESHOLDS["WEBSITE_EXACT"]

        # 4. Address Similarity (Weight: 15%)
        if b1.full_address and b2.full_address:
            addr_score = fuzz.token_set_ratio(
                b1.full_address.lower(), b2.full_address.lower()
            ) / 100.0
            score += addr_score * DEDUPE_THRESHOLDS["ADDRESS_SIMILARITY"]

        # 5. Social Exact Match (Weight: 10%)
        socials1 = {
            self.clean_url(b1.instagram_url),
            self.clean_url(b1.facebook_url),
            self.clean_url(b1.linkedin_url)
        } - {""}
        socials2 = {
            self.clean_url(b2.instagram_url),
            self.clean_url(b2.facebook_url),
            self.clean_url(b2.linkedin_url)
        } - {""}

        if socials1 and socials2 and socials1.intersection(socials2):
            score += DEDUPE_THRESHOLDS["SOCIAL_EXACT"]

        return score

    def find_duplicates(self, records: List[BusinessSchema]) -> List[List[BusinessSchema]]:
        """Groups a list of business records into clusters of duplicates."""
        clusters = []
        visited = set()

        # Dedupe within same city only
        city_groups = {}
        for r in records:
            city_groups.setdefault(r.city.lower(), []).append(r)

        for city, city_records in city_groups.items():
            for i, record_i in enumerate(city_records):
                if id(record_i) in visited:
                    continue

                current_cluster = [record_i]
                visited.add(id(record_i))

                for j in range(i + 1, len(city_records)):
                    record_j = city_records[j]
                    if id(record_j) in visited:
                        continue

                    sim_score = self.calculate_similarity(record_i, record_j)
                    if sim_score >= DEDUPE_THRESHOLDS["MATCH_CONFIDENCE_MIN"]:
                        current_cluster.append(record_j)
                        visited.add(id(record_j))

                clusters.append(current_cluster)

        return clusters
