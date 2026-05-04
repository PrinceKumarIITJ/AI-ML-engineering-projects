"""
The Data Cleaner (Normalizer).
Different websites provide data in different shapes (e.g., Google Maps might have 'Phone', 
JustDial might have 'Mobile'). This script forces all data to wear the same "uniform" 
so it fits perfectly into our database and Excel sheets.
"""
import logging
from typing import Dict, Any
from models.schema import BusinessSchema

logger = logging.getLogger(__name__)

class Normalizer:
    @staticmethod
    def normalize(data: Dict[str, Any]) -> BusinessSchema:
        """
        Takes a messy dictionary of data and cleans it up.
        It removes extra spaces, fills in blanks with 'Unknown', 
        and ensures lists (like 'services_offered') don't have duplicates.
        """
        # Ensure mandatory fields are present
        if not data.get('business_name'):
            data['business_name'] = "Unknown Business"
        if not data.get('city'):
            data['city'] = "Unknown City"

        # Clean string fields
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip() if v.strip() else None

        # Normalize specific complex fields
        if 'services_offered' in data and isinstance(data['services_offered'], list):
            data['services_offered'] = list(set([
                s.strip() for s in data['services_offered'] if s and s.strip()
            ]))
        else:
            data['services_offered'] = []

        if 'source_platforms' in data and isinstance(data['source_platforms'], list):
            data['source_platforms'] = list(set([p.strip() for p in data['source_platforms'] if p]))
        else:
            data['source_platforms'] = []

        if 'source_urls' in data and isinstance(data['source_urls'], list):
            data['source_urls'] = list(set([u.strip() for u in data['source_urls'] if u]))
        else:
            data['source_urls'] = []

        return BusinessSchema(**data)
