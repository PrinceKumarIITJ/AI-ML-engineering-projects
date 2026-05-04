"""
The Quality Assurance Agent (Validator).
This script checks the work of the other agents. It looks at phone numbers, 
emails, and websites to make sure they aren't fake or misspelled. 
If it finds a 5-digit phone number, it deletes it. It also grades the lead 
giving it a "Verified", "Enriched", or "Raw" score based on how much good data it has.
"""
import re
import logging
from typing import List
from models.schema import BusinessSchema

logger = logging.getLogger(__name__)

class Validator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Checks if an email has an '@' and a domain (like .com)."""
        if not email: return False
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        if not phone: return False
        digits = re.sub(r'\D', '', phone)
        # Indian phone numbers should be at least 10 digits
        return len(digits) >= 10

    @staticmethod
    def validate_url(url: str) -> bool:
        if not url: return False
        try:
            pattern = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
                r'localhost|' # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return re.match(pattern, url) is not None
        except Exception:
            return False

    @classmethod
    def validate_record(cls, record: BusinessSchema) -> BusinessSchema:
        """
        Validates individual fields and sets the overall confidence score.
        If a field is invalid based on regex (e.g. malformed email), it is set to None.
        """
        if record.email and not cls.validate_email(record.email):
            record.email = None
            
        if record.contact_number and not cls.validate_phone(record.contact_number):
            record.contact_number = None

        if record.website and not cls.validate_url(record.website):
            # Sometimes it's just missing http://
            if record.website and not record.website.startswith('http'):
                record.website = f"http://{record.website}"
                if not cls.validate_url(record.website):
                    record.website = None
            else:
                record.website = None

        # Confidence Scoring Logic
        has_contact = bool(record.contact_number or record.email)
        has_social = bool(record.instagram_url or record.facebook_url or record.linkedin_url or record.website)
        has_address = bool(record.full_address)
        
        # Determine confidence
        if has_contact and has_social and has_address:
            record.confidence_score = "verified"
        elif has_contact and (has_social or has_address):
            record.confidence_score = "enriched"
        elif has_contact or has_social or has_address:
            record.confidence_score = "raw"
        else:
            record.confidence_score = "low_confidence"

        return record

    @classmethod
    def run_pipeline(cls, records: List[BusinessSchema]) -> List[BusinessSchema]:
        logger.info(f"Validating and scoring {len(records)} records...")
        return [cls.validate_record(r) for r in records]
