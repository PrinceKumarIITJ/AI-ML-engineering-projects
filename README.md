# 🚀 IntelliLead: B2B Intelligence & Lead Mining Platform

An AI-powered, industrial-grade data mining platform designed to extract, clean, enrich, and deduplicate high-quality business leads (focusing on the Event Management and Wedding industry) across major Indian cities. 

This system transforms noisy, unstructured web data into a refined, deduplicated directory of verified business entities. It features autonomous stealth scraping, NLP-based relevance filtering, and rapid fuzzy-logic deduplication.

---

## 🌟 Key Features & Performance
- **Massive Scale**: Capable of mining tens of thousands of raw records autonomously.
- **Multi-Source Intelligence**: Extracts data simultaneously from **Google Maps, WedMeGood, WeddingWire India, JustDial, and IndiaMART**.
- **Stealth Evasion**: Integrated `playwright-stealth` and specific HTTP protocol downgrades to bypass advanced bot mitigation systems (like Cloudflare).
- **AI-Powered Verification**: Utilizes local `Sentence-Transformers` (`all-MiniLM-L6-v2`) to semantically classify leads, instantly rejecting false positives (e.g., classifying a "Caterer" vs. a full "Event Planner").
- **Smart Deduplication**: A custom fuzzy-logic matcher clusters fragmented records across different platforms into single, enriched Master Profiles.
- **Deep Web Enrichment**: Automatically queries search engines to find missing contact numbers or Instagram URLs for high-value leads.
- **Premium UI Dashboard**: A sleek, web-based Streamlit dashboard for real-time analytics and report generation.

---

## 📁 System Architecture & Directory Structure

```bash
IntelliLead/
├── main.py                 # The Supreme Orchestrator (Runs the entire pipeline)
├── app.py                  # Streamlit Web Dashboard UI
├── config.py               # Global rulebook (Keywords, Cities, Dedupe Thresholds)
├── demo_run.py             # A lightweight, 60-second execution script for presentations
├── requirements.txt        # Python dependencies
├── data/                   # Persistent SQLite storage (Crash-recovery & Lead Database)
├── outputs/                # Generated Excel Reports
├── models/                 # Core Intelligence Engines
│   ├── schema.py             # Pydantic data blueprint
│   ├── database.py           # SQLite checkpoint and persistence manager
│   ├── duplicate_matcher.py  # RapidFuzz logic for identifying duplicate companies
│   └── relevance_classifier.py # SBERT AI model for filtering bad leads
├── pipelines/              # Data Processing Workflows
│   ├── normalize.py          # Data cleaner and standardizer
│   ├── dedupe.py             # Cluster resolution and merging
│   ├── enrich.py             # DuckDuckGo and Deep Web social media discovery
│   ├── validate.py           # Regex-based Quality Assurance (Phones, Emails)
│   └── export_excel.py       # Excel generation with styling and city tabs
└── scrapers/               # Stealth Data Acquisition Bots
    ├── base_scraper.py       # Base class with Playwright stealth configurations
    ├── google_maps.py        # Google Maps DOM parser
    └── other_platforms.py    # Custom parsers for JustDial, WedMeGood, etc.
```

---

## 🚀 Full Execution Guide

Follow these exact steps to set up and execute the IntelliLead platform on your local machine.

### Step 1: Prerequisites
Ensure you have the following installed:
- **Python 3.10 or higher** (Ensure Python is added to your system PATH).
- **Git** (To clone or manage the repository).

### Step 2: Environment Setup
Open your terminal (PowerShell or Command Prompt) and navigate to the project directory:

```bash
# Install all required Python packages
pip install -r requirements.txt

# Install Playwright browser binaries (Required for the Stealth Scrapers)
playwright install chromium
```

### Step 3: Configure Your Targets
Before running, you can adjust the targets in `config.py`. 
Open `config.py` and modify the `TARGET_CITIES` or `TARGET_KEYWORDS` lists to suit your immediate needs.

### Step 4: Running the Platform
You have three different ways to run IntelliLead, depending on your goal.

#### Option A: The Quick Presentation Demo (Recommended First Step)
If you just want to see the system work instantly (under 60 seconds):
```bash
python demo_run.py
```
*This will scrape exactly 5 leads from Jaipur, process them through the AI, and generate a `Demo_Leads_Report.xlsx` file in the `outputs/` folder.*

#### Option B: The Full Production Mining Job
To run the massive, multi-city extraction (this can take hours depending on your config):
```bash
python main.py
```
*The system will autonomously launch stealth browsers, extract data, save checkpoints (so you can safely pause/resume), and build the master database.*

#### Option C: The UI Dashboard
To view the analytics and download reports visually:
```bash
streamlit run app.py
```
*This will open a beautiful web dashboard in your default browser.*

---

## 🛑 Troubleshooting & Maintenance
- **Playwright Errors**: If the scrapers fail to launch, ensure you ran `playwright install chromium`.
- **Database Locks**: If you get an `OperationalError: database is locked`, ensure you don't have multiple instances of `main.py` or `demo_run.py` running simultaneously.
- **Model Downloads**: The very first time you run the script, it will download the SBERT AI model (~90MB). Ensure you have an active internet connection.

---

## 🔐 Security & Integrity
- **Zero Hallucination**: The system relies strictly on DOM parsing and deterministic web discovery. No generative AI is used to "guess" phone numbers.
- **Checkpoint Recovery**: The system tracks its exact progress. If your Wi-Fi drops, simply rerun `python main.py`, and it will resume exactly where it left off.
