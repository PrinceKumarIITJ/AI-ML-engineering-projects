import os
from pipelines.normalize import Normalizer
from models.relevance_classifier import RelevanceClassifier
from pipelines.dedupe import Deduplicator
from pipelines.validate import Validator
from pipelines.export_excel import ExcelExporter

raw_data = [
    {
        "business_name": "Royal Event Planners",
        "city": "Jodhpur",
        "contact_number": "+91 9876543210",
        "website": "www.royaleventsjodhpur.com",
        "services_offered": ["wedding", "corporate"],
        "source_platforms": ["Google Maps"],
    },
    {
        "business_name": "Royal Events & Co.", # Should deduplicate with above
        "city": "Jodhpur",
        "contact_number": "9876543210", # exact match on normalized phone
        "instagram_url": "https://instagram.com/royaleventsjodhpur",
        "services_offered": ["decorators"],
        "source_platforms": ["Justdial"],
    },
    {
        "business_name": "Jodhpur Venue & Banquets", # Should be filtered out by irrelevant keyword
        "city": "Jodhpur",
        "contact_number": "9998887776",
        "source_platforms": ["WedMeGood"]
    }
]

print("1. Normalizing...")
normalized = [Normalizer.normalize(r) for r in raw_data]

print("2. Classifying Relevance...")
classifier = RelevanceClassifier()
relevant_only = []
for idx, r in enumerate(normalized):
    r = classifier.classify(r)
    print(f"  [{idx}] {r.business_name} -> Relevant: {r.is_relevant} ({r.relevance_reason})")
    if r.is_relevant:
        relevant_only.append(r)

print("3. Deduplicating...")
deduplicator = Deduplicator()
deduped = deduplicator.process_records(relevant_only)
print(f"  Records reduced from {len(relevant_only)} to {len(deduped)}")

for d in deduped:
    print(f"    - {d.business_name} (Phone: {d.contact_number}, Insta: {d.instagram_url})")

print("4. Validating...")
validated = Validator.run_pipeline(deduped)
for v in validated:
    print(f"    - Confidence: {v.confidence_score}")

print("5. Exporting...")
exporter = ExcelExporter("Test_Output.xlsx")
exporter.export(validated)
print(f"Done! File generated at {exporter.filepath}")
