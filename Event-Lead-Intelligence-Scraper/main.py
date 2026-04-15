import sys
import logging
import time
import argparse
from typing import List, Dict, Any

from config import TARGET_CITIES, TARGET_KEYWORDS, DB_PATH
from models.database import DatabaseManager
from scrapers.google_maps import GoogleMapsScraper
from scrapers.other_platforms import (
    WedMeGoodScraper, 
    IndiaMartScraper, 
    JustDialScraper, 
    WeddingWireScraper, 
    GoogleSearchScraper,
    TheWeddingCompanyScraper
)
from pipelines.normalize import Normalizer
from models.relevance_classifier import RelevanceClassifier
from pipelines.dedupe import Deduplicator
from pipelines.enrich import DataEnricher
from pipelines.validate import Validator
from pipelines.export_excel import ExcelExporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ScraperOrchestrator:
    def __init__(self):
        self.db = DatabaseManager(DB_PATH)
        self.classifier = RelevanceClassifier()
        self.deduplicator = Deduplicator()
        self.enricher = DataEnricher()
        self.exporter = ExcelExporter()
        
        # Initialize scrapers (lazy instantiation)
        self.scraper_classes = [
            GoogleMapsScraper,
            WedMeGoodScraper,
            WeddingWireScraper,
            JustDialScraper,
            IndiaMartScraper,
            GoogleSearchScraper,
            TheWeddingCompanyScraper
        ]

    def _process_raw_batch(self, raw_data_list: List[Dict[str, Any]]) -> List[Any]:
        """Passes a scraped batch through the NLP and Validation pipeline."""
        processed = []
        for raw_dict in raw_data_list:
            try:
                # 1. Normalize
                schema_obj = Normalizer.normalize(raw_dict)
                
                # 2. Add to batch
                processed.append(schema_obj)
            except Exception as e:
                logger.error(f"Error normalizing record: {e}")
                
        # 3. NLP Relevance Classification (Batch)
        return self.classifier.classify_batch(processed)

    def run_mining_job(self, cities: List[str] = TARGET_CITIES, keywords: List[str] = TARGET_KEYWORDS):
        logger.info(f"Starting Multi-Platform Mining Job for {len(cities)} cities and {len(keywords)} keywords...")
        
        for city in cities:
            logger.info(f"\n{'='*50}\nStarting Data Gathering for {city.upper()}\n{'='*50}")
            
            for keyword in keywords:
                for ScraperClass in self.scraper_classes:
                    scraper = ScraperClass(headless=True)
                    platform = scraper.platform_name
                    
                    if self.db.is_checkpoint_completed(city, platform, keyword):
                        logger.info(f"Skipping {platform} for '{keyword}' in {city} (Already Completed)")
                        continue
                        
                    logger.info(f"Launching {platform} scraper for '{keyword}' in {city}...")
                    try:
                        # 1. Scrape (Limit 300 per city/keyword/platform combo to easily hit 5000+ total)
                        raw_data = scraper.scrape(keyword, city, limit=300)
                        
                        if raw_data:
                            # 2. Normalize and Filter Relevance
                            clean_records = self._process_raw_batch(raw_data)
                            
                            # 3. Save raw leads to Database
                            self.db.save_leads_batch(clean_records, platform)
                            logger.info(f"Saved {len(clean_records)} relevant leads from {platform} to DB.")
                        
                        # Mark completed
                        self.db.update_checkpoint(city, platform, keyword, last_page=0, status="completed")
                        
                    except Exception as e:
                        logger.error(f"Scraper {platform} failed for {city}: {e}")
                    finally:
                        # Ensure browser closes safely between heavy loads
                        scraper.close()
                        time.sleep(2)

    def run_post_processing_pipeline(self):
        """Runs deduplication, enrichment, and validation on all database records."""
        logger.info(f"\n{'='*50}\nStarting Post-Processing Intelligence Pipeline\n{'='*50}")
        
        all_records = self.db.load_all_leads()
        if not all_records:
            logger.error("No records found in database! Run mining job first.")
            return

        logger.info(f"Loaded {len(all_records)} raw relevant records from database.")
        
        # 1. Deduplicate Global
        deduped = self.deduplicator.process_records(all_records)
        
        # 2. Enrich
        enriched = self.enricher.run_pipeline(deduped)
        
        # 3. Validate & Confidence Score
        validated = Validator.run_pipeline(enriched)
        
        # 4. Generate Final Excel
        self.exporter.export(validated)
        logger.info(f"Data Pipeline Complete! Master database saved to {self.exporter.filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Source B2B Lead Scraper")
    parser.add_argument("--process-only", action="store_true", help="Skip scraping and run dedupe/enrich pipeline on DB records only")
    args = parser.parse_args()

    orchestrator = ScraperOrchestrator()
    
    if args.process_only:
        orchestrator.run_post_processing_pipeline()
    else:
        # Full Job
        orchestrator.run_mining_job()
        orchestrator.run_post_processing_pipeline()
