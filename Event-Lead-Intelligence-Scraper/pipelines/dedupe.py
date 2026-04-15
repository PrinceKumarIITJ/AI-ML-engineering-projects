import logging
from typing import List
from models.schema import BusinessSchema
from models.duplicate_matcher import DuplicateMatcher

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self):
        self.matcher = DuplicateMatcher()

    def process_records(self, records: List[BusinessSchema]) -> List[BusinessSchema]:
        """
        Takes a raw list of BusinessSchemas, groups duplicates, and merges each cluster
        into a single consolidated record.
        """
        clusters = self.matcher.find_duplicates(records)
        deduped_records = []
        
        for cluster in clusters:
            if not cluster:
                continue
                
            # Start with the first record in cluster
            merged_record = cluster[0]
            
            # Merge the rest
            if len(cluster) > 1:
                merged_record.duplicate_resolution_id = f"MERGED_{len(cluster)}_RECORDS"
                for record in cluster[1:]:
                    merged_record = merged_record.merge(record)
                    
            deduped_records.append(merged_record)
            
        logger.info(f"Deduplication: Reduced {len(records)} raw records down to {len(deduped_records)} unique entities.")
        return deduped_records
