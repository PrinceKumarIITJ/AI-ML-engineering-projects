"""
Relevance Classifier — uses a combination of keyword heuristics and
sentence-transformer semantic similarity to filter out businesses that
are NOT event management / wedding planning companies.
"""
import re
import logging
from typing import List
from .schema import BusinessSchema

logger = logging.getLogger(__name__)

# Businesses containing these keywords in name/services are likely NOT event planners
IRRELEVANT_KEYWORDS = [
    "banquet hall", "banquet", "hotel", "resort", "farmhouse",
    "caterer", "catering service", "photographer", "photography studio",
    "dj service", "makeup artist", "mehandi", "mehndi",
    "tent house", "flower shop", "florist", "gift shop",
    "invitation card", "printing press", "travel agent",
    "real estate", "car rental", "jeweller", "boutique",
    "sweet shop", "restaurant", "dhaba", "hospital", "clinic",
]

# Strong positive signals
RELEVANT_KEYWORDS = [
    "event management", "event planner", "wedding organiser", "wedding organizer",
    "wedding planner", "event coordinator", "wedding management",
    "event organiser", "event organizer", "wedding consultant",
    "event company", "wedding company", "destination wedding",
    "corporate event", "event solution", "wedding decoration and planning",
    "event & wedding", "wedding & event",
]

# Try to import sentence-transformers; fall back to keyword-only if unavailable
_USE_SEMANTIC = False
_model = None
_relevant_embeddings = None

def _init_semantic_model():
    """Lazy-load the sentence-transformer model."""
    global _USE_SEMANTIC, _model, _relevant_embeddings
    try:
        from sentence_transformers import SentenceTransformer, util
        from config import MODEL_NAME
        _model = SentenceTransformer(MODEL_NAME)
        _relevant_embeddings = _model.encode(RELEVANT_KEYWORDS, convert_to_tensor=True)
        _USE_SEMANTIC = True
        logger.info("Semantic relevance model loaded successfully.")
    except Exception as e:
        logger.warning(f"Sentence-transformers not available, using keyword-only classification: {e}")
        _USE_SEMANTIC = False


class RelevanceClassifier:
    def __init__(self):
        # Lazy init on first use
        if _model is None:
            _init_semantic_model()

    def classify(self, business: BusinessSchema) -> BusinessSchema:
        """Determines if a business is a relevant Event Management / Wedding Organiser."""

        name_lower = business.business_name.lower()
        services = " ".join([s.lower() for s in business.services_offered])
        category_lower = (business.category or "").lower()
        desc = f"{name_lower} {services} {category_lower}"

        # ── 1. Negative Heuristics (Rule-based) ──
        for junk in IRRELEVANT_KEYWORDS:
            if re.search(rf'\b{re.escape(junk)}\b', desc):
                # Spare if name clearly says "events" or "planner"
                if any(kw in name_lower for kw in ("event", "planner", "wedding planner")):
                    continue
                business.is_relevant = False
                business.relevance_reason = f"Irrelevant keyword: {junk}"
                return business

        # ── 2. Positive Heuristics (Rule-based) ──
        for rel in RELEVANT_KEYWORDS:
            if rel in desc:
                business.is_relevant = True
                business.relevance_reason = f"Relevant keyword: {rel}"
                return business

        # ── 3. Semantic Similarity fallback ──
        if _USE_SEMANTIC and _model is not None:
            try:
                from sentence_transformers import util
                text_emb = _model.encode(desc, convert_to_tensor=True)
                cosine_scores = util.cos_sim(text_emb, _relevant_embeddings)[0]
                max_score = float(cosine_scores.max())

                if max_score > 0.60:
                    business.is_relevant = True
                    business.relevance_reason = f"Semantic similarity: {max_score:.2f}"
                else:
                    business.is_relevant = False
                    business.relevance_reason = f"Low semantic similarity: {max_score:.2f}"
                return business
            except Exception as e:
                logger.debug(f"Semantic check failed: {e}")

        # ── 4. Default: accept if no strong negative signal ──
        # If we can't determine, keep it (better to have a false positive than miss data)
        business.is_relevant = True
        business.relevance_reason = "No strong negative signal found"
        return business

    def classify_batch(self, records: List[BusinessSchema]) -> List[BusinessSchema]:
        """Classify and filter a batch, returning only relevant records."""
        relevant = []
        for r in records:
            r = self.classify(r)
            if r.is_relevant:
                relevant.append(r)
        logger.info(f"Relevance filter: {len(relevant)}/{len(records)} passed")
        return relevant
