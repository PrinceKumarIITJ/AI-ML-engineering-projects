from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BusinessSchema(BaseModel):
    """Unified schema for every business record regardless of source platform."""

    # Core Identity
    business_name: str
    category: str = "Event Management"
    subcategory: Optional[str] = None

    # Location
    city: str
    state: str = "Unknown"
    full_address: Optional[str] = None
    pincode: Optional[str] = None

    # Contact
    contact_number: Optional[str] = None
    alternate_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Social & Links
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    google_maps_url: Optional[str] = None

    # Reputation & Quality
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_range: Optional[str] = None
    services_offered: List[str] = Field(default_factory=list)
    years_in_business: Optional[int] = None

    # Traceability
    source_platforms: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)

    # System Metadata
    confidence_score: str = "raw"  # verified, enriched, raw, low_confidence
    duplicate_resolution_id: Optional[str] = None
    last_verified_timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())

    # NLP & Relevance metadata
    is_relevant: bool = True
    relevance_reason: str = ""

    def merge(self, other: "BusinessSchema") -> "BusinessSchema":
        """Merge another business schema into this one, keeping the most complete data."""
        data = self.model_dump()
        other_data = other.model_dump()

        for k, v in other_data.items():
            if k in ("last_verified_timestamp", "is_relevant", "relevance_reason"):
                continue
            current = data.get(k)
            # Fill empty fields from other
            if v and not current:
                data[k] = v
            # Merge lists (deduplicated)
            elif isinstance(v, list) and isinstance(current, list):
                merged = list(current)
                for item in v:
                    if item not in merged:
                        merged.append(item)
                data[k] = merged

        # Prefer longer (usually more descriptive) business name
        if other.business_name and len(other.business_name) > len(self.business_name):
            data['business_name'] = other.business_name

        # Keep higher rating
        if other.rating and (not self.rating or other.rating > self.rating):
            data['rating'] = other.rating
        # Keep higher review count
        if other.review_count and (not self.review_count or other.review_count > self.review_count):
            data['review_count'] = other.review_count

        data['last_verified_timestamp'] = datetime.utcnow()
        return BusinessSchema(**data)
