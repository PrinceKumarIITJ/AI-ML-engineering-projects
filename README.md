# Event Lead Intelligence Scraper

An AI-powered, industrial-grade data mining platform designed to extract, clean, and enrich high-quality business leads for the event management and wedding industry across 9 major Indian cities.

This system transforms noisy web data into a refined, deduplicated directory of verified business entities, far exceeding the initial 5,000-lead target by mining **31,500+ raw records**.

## Performance Milestones
- **Mining Job Status**: COMPLETED
- **Total Raw Leads**: 31,508
- **Unique Business Entities**: 24,597 (Post-Deduplication)
- **Top Quality Deliverable**: 5,000 Premium leads (Sorted by rating/verification).
- **City Coverage**: Jaipur, Delhi, Indore, Gurgaon, Noida, Chandigarh, Jodhpur, Bhopal, Udaipur.

## Intelligence Stack

### 1. Multi-Source Scraping Engine
Robust scraping pipelines for **Google Maps, WedMeGood, WeddingWire India,** and **IndiaMART**.
- **Stealth Evasion**: Integrated `playwright-stealth` and forced `HTTP/1.1` protocol to bypass advanced bot detection.
- **Auto-Retry & Checkpointing**: Ensures stability during large-scale city-wise mining operations.

### 2. AI-Powered Verification
- **Semantic Classification**: Uses the `all-MiniLM-L6-v2` SBERT model to filter out irrelevant listings (e.g., hotels/banppets) based on business names and services.
- **Weighted Deduplication**: A custom fuzzy-logic matcher (handling Name, Phone, and Address) that clusters records from different platforms into a single consolidated master profile.

### 3. Intelligence Pipeline
- **Parallel Enrichment**: High-speed web discovery using `ThreadPoolExecutor` to verify social media digital footprints (Instagram, Facebook, LinkedIn).
- **Quality Ranking**: A tiered sorting algorithm that prioritizes verified businesses with high ratings and complete contact information.

## Final Deliverable
The output is generated as an optimized Excel Master Database with city-wise tabs and a summary dashboard.
- **Location**: `outputs/Wedding_Event_Companies_Master.xlsx`

## Repository Structure
```bash
├── data/           # Persistent SQLite storage for mined leads
├── models/         # AI logic (Relevance, Deduplication, Schema)
├── pipelines/      # Intelligence workflow (Enrich, Validate, Export)
├── scrapers/       # Platform-specific scraping logic
└── main.py         # Primary orchestration entry point
```

## Getting Started

### Prerequisites
- Python 3.10+
- Chrome/Chromium (for Playwright)

### Setup
1. **Clone & Install**:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```
2. **Execute Job**:
   ```bash
   python main.py
   ```
3. **Run Intelligence Pipeline (Process only)**:
   ```bash
   python main.py --process-only
   ```

## 🔐 Security & Integrity
- **No Hallucination**: Strict verification policies ensure only real scraped data is populated.
- **Optimized Performance**: Parallel processing for I/O bound data enrichment.
