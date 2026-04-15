import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.absolute()
DB_PATH = BASE_DIR / "data" / "leads.sqlite"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
os.makedirs(DB_PATH.parent, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Target Audience
TARGET_CITIES = [
    "Jaipur", "Jodhpur", "Udaipur", "Delhi", "Gurgaon",
    "Noida", "Chandigarh", "Indore", "Bhopal"
]

TARGET_KEYWORDS = [
    "Event Management Companies",
    "Wedding Organisers",
    "Wedding Planners",
    "Event Planners",
    "Wedding Decorators and Planners",
    "Event Organizers",
]

# Scraper Settings
MAX_RETRIES = 3
BASE_DELAY = 2.0  # seconds
BATCH_SIZE = 50   # records before flushing to DB
SCROLL_PAUSE = 2.0  # seconds between scrolls

# Playwright timeouts
PAGE_TIMEOUT = 60000  # ms
SELECTOR_TIMEOUT = 15000  # ms

# Rotating User-Agents (to avoid fingerprinting)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
]

# Duplication Weights
DEDUPE_THRESHOLDS = {
    "NAME_SIMILARITY": 0.35,
    "PHONE_EXACT": 0.25,
    "WEBSITE_EXACT": 0.15,
    "ADDRESS_SIMILARITY": 0.15,
    "SOCIAL_EXACT": 0.10,
    "MATCH_CONFIDENCE_MIN": 0.80
}

# Relevance Classification Model (Local)
MODEL_NAME = "all-MiniLM-L6-v2"

# Excel column order for final output
EXCEL_COLUMNS = [
    "S.No",
    "Business Name",
    "Category",
    "City",
    "State",
    "Full Address",
    "Pincode",
    "Contact Number",
    "Alternate Number",
    "Email",
    "Website",
    "Instagram",
    "Facebook",
    "LinkedIn",
    "Google Maps Link",
    "Rating",
    "Reviews",
    "Price Range",
    "Services Offered",
    "Years in Business",
    "Source Platforms",
    "Confidence Score",
]
