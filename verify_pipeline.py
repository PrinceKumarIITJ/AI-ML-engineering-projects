from main import ScraperOrchestrator
import logging

logging.basicConfig(level=logging.INFO)

def verify():
    print("--- Starting Pipeline Verification (Test Batch) ---")
    orchestrator = ScraperOrchestrator()
    
    # Target only one city and one keyword for speed
    test_cities = ["Chandigarh"]
    test_keywords = ["Wedding Planners"]
    
    # 1. Run limited mining
    # Note: I'll manually call the scrapers with a small limit since run_mining_job has a hardcoded limit of 300
    for ScraperClass in orchestrator.scraper_classes:
        scraper = ScraperClass(headless=True)
        platform = scraper.platform_name
        print(f"Testing {platform}...")
        try:
            raw_data = scraper.scrape(test_keywords[0], test_cities[0], limit=5)
            if raw_data:
                clean_records = orchestrator._process_raw_batch(raw_data)
                orchestrator.db.save_leads_batch(clean_records, platform)
                print(f"Success: Found {len(clean_records)} leads from {platform}")
            else:
                print(f"Notice: No data found for {platform}")
        except Exception as e:
            print(f"Error in {platform}: {e}")
        finally:
            scraper.close()
            
    # 2. Run post-processing
    print("--- Running Post-Processing ---")
    orchestrator.run_post_processing_pipeline()
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify()
