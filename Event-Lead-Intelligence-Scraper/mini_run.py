from scrapers.google_maps import GoogleMapsScraper
from pipelines.normalize import Normalizer
from models.relevance_classifier import RelevanceClassifier
from pipelines.dedupe import Deduplicator
from pipelines.validate import Validator
from pipelines.export_excel import ExcelExporter
import logging

logging.basicConfig(level=logging.INFO)

print("Starting Mini-Scrape to Generate Initial Data Sample...")

s1 = GoogleMapsScraper(headless=True)
data1 = s1.scrape("Event Planners", "Jodhpur", limit=10)

print(f"Scraped {len(data1)} raw records.")

normed = [Normalizer.normalize(r) for r in data1]

classifier = RelevanceClassifier()
relevant = classifier.classify_batch(normed)

deduper = Deduplicator()
deduped = deduper.process_records(relevant)

validator = Validator()
validated = validator.run_pipeline(deduped)

exporter = ExcelExporter("Sample_Intelligence.xlsx")
exporter.export(validated)
print(f"Exported successfully to {exporter.filepath}")
