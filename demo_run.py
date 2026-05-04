"""
This script runs a very small, fast version of the main project.
Instead of searching multiple cities for thousands of leads, it 
searches just one city (Jaipur) for 5 leads. It is used to quickly 
demonstrate to management how the AI agent works end-to-end.
"""
import sys
import logging
import time
from typing import List, Dict, Any

from models.database import DatabaseManager
from scrapers.google_maps import GoogleMapsScraper
from pipelines.normalize import Normalizer
from models.relevance_classifier import RelevanceClassifier
from pipelines.dedupe import Deduplicator
from pipelines.validate import Validator
from pipelines.export_excel import ExcelExporter
from config import DB_PATH

# Setup logging to be very visible for the demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DEMO")

def run_quick_demo():
    print("\n" + "="*60)
    print(" INTELLILEAD AGENTIC PIPELINE: QUICK DEMONSTRATION")
    print("="*60)
    print("Goal: Scrape, Clean, and Export a few leads in < 60 seconds.")
    print("Note: Running in HEADLESS mode for compatibility.")
    print("="*60 + "\n")

    # 1. Setup
    db = DatabaseManager(DB_PATH)
    
    # We'll use the classifier but note it might take a sec to load the first time
    print("[1/5] Initializing AI Relevance Engine (SBERT)...")
    classifier = RelevanceClassifier()
    
    # 2. Mining (Limited to 5 results for speed)
    city = "Jaipur"
    keyword = "Wedding Planners"
    print(f"[2/5] Launching Autonomous Scraper for '{keyword}' in {city}...")
    
    # We set headless=True for compatibility with this environment
    scraper = GoogleMapsScraper(headless=True)
    try:
        raw_data = scraper.scrape(keyword, city, limit=5)
        print(f" SUCCESS: Captured {len(raw_data)} raw records from the live web.")
        
        # 3. Processing
        print("[3/5] Passing data through the Intelligence Pipeline...")
        processed = []
        for d in raw_data:
            norm = Normalizer.normalize(d)
            processed.append(norm)
        
        # Filter relevance
        clean_records = classifier.classify_batch(processed)
        print(f" SUCCESS: AI Relevance Filter: {len(clean_records)}/{len(processed)} leads verified as relevant.")
        
        # 4. Deduplication & Export
        print("[4/5] Deduplicating and Preparing Final Report...")
        deduper = Deduplicator()
        unique = deduper.process_records(clean_records)
        
        validator = Validator()
        validated = validator.run_pipeline(unique)
        
        # Export to a special demo file
        demo_exporter = ExcelExporter("Demo_Leads_Report.xlsx")
        demo_exporter.export(validated)
        
        print(f"\n" + "="*60)
        print(" DEMO COMPLETED SUCCESSFULLY")
        print(f" Database Updated: {DB_PATH}")
        print(f" Final Report Generated: Demo_Leads_Report.xlsx")
        print("="*60)
        print("\nYou can now show the Excel file to the company or run 'streamlit run app.py' to show the dashboard.")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    run_quick_demo()
