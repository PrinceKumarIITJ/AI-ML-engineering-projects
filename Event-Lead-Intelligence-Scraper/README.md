# Event Lead Intelligence Scraper

An intelligent, AI-powered system designed to scrape, clean, and enrich business data for the event management and wedding planning industry. This tool ensures high data accuracy by eliminating duplicates and scouting the digital footprints of businesses to fill missing information.

## System Overview

The project is built to transform raw, noisy web data into a refined directory of verified business leads. It focuses on the specific niche of event management, ensuring that users only receive data that is relevant to their requirements.

### Key Features

#### 1. AI-Powered Relevance Filtering
The system uses **Sentence-Transformers (SBERT)** to perform semantic analysis on every scraped business. Instead of simple keyword matching, the AI understands the context of the business name and service descriptions.
- **Goal:** Eliminate "junk data" such as hotels, banquets, or caterers that might appear in search results but are not primary event planners.
- **Mechanism:** Semantic similarity scoring against industry-specific embeddings.

#### 2. Intelligent Deduplication and Merging
To provide a non-redundant database, the system identifies identical entities across multiple platforms (e.g., Google Maps and listing directories).
- **Goal:** Return only unique entities.
- **Mechanism:** Fuzzy matching of business names, addresses, and contacts to group duplicates into a single consolidated master record.

#### 3. Digital Footprint Enrichment
For records with missing information (such as websites or social media links), the system acts as a scout to find the missing data elsewhere on the internet.
- **Goal:** Fill gaps without introducing inaccurate data.
- **Mechanism:** 
    - Automated search engine discovery via DuckDuckGo to avoid scraping blocks.
    - Deep-crawling of identified official websites to extract social media handles (Instagram, Facebook, LinkedIn).

#### 4. Data Integrity Policy
The system follows a strict "No Hallucination" policy. If a field cannot be found through official digital footprints, it is left empty. This prevents the insertion of junk or placeholder data.

## System Architecture

The tool is organized into a modular pipeline:
- **Scrapers:** Modular scripts for target platforms.
- **Models:** AI logic for relevance and duplicate detection.
- **Pipelines:**
    - **Normalize:** Formats raw data for consistency.
    - **Validate:** Sanitizes fields (phone numbers, URLs).
    - **Dedupe:** Merges redundant records.
    - **Enrich:** Scouts the internet for missing fields.
- **Export:** Generates clean Excel or Database outputs.

## Getting Started

### Prerequisites
- Python 3.9+
- Pip (Python Package Manager)

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the semantic model:
   The system will automatically download the required SBERT model (all-MiniLM-L6-v2) on the first run.

### Usage
Run the main application interface:
```bash
python app.py
```

## Technical Details

- **NLP Model:** HuggingFace `all-MiniLM-L6-v2` for semantic similarity.
- **Search Engine:** Privacy-respecting search APIs for digital footprint scouting.
- **Data Storage:** Optimized SQLite databases locally for persistence and checkpointing.
