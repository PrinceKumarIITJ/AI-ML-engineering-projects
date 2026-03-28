#  Startup Data Profiler + API

This project scrapes startup data from [Growjo](https://growjo.com), cleans and transforms it, generates insights and visualizations, and exposes the insights via a RESTful API using FastAPI.

---

##  Project Overview

-  **Web Scraping** — Scrapes data like company name, industry, revenue, growth % from Growjo.
-  **Data Cleaning** — Cleans nulls, removes duplicates, converts revenue and growth fields to numeric format.
-  **Visualization** — Creates distribution plots for industries, revenue, and growth.
-  **REST API** — Exposes key data summaries and queries via FastAPI.

---

##  Setup Instructions

###  Prerequisites

- Python 3.8 or above
- pip
---

###  1. Clone the repository

```
git clone <your-repo-url>
cd startup-data-profiler 
```
---

###  2. Create and activate virtual environment

 - **Create virtual environment**
```
python -m venv venv
```
- **Activate (Windows)**
```
venv\Scripts\activate
```
 - **Activate (macOS/Linux)**
```
source venv/bin/activate
```
---
### 3. Install dependencies
```
pip install -r requirements.txt
```
---

###  How to Run the Project
 - Step 1: Run the scraper
```
python scraper.py
```
 - Step 2: Clean the data and generate visualizations
```
python cleanser.py
```
 - Step 3: Start the FastAPI server
```
uvicorn app:app --reload
```
---
**Then go to:**

http://127.0.0.1:8000/docs for Swagger UI

http://127.0.0.1:8000/summary to see the summary data

---

###  API Usage
| Endpoint                 | Description                                  |
| ------------------------ | -------------------------------------------- |
| `/`                      | Welcome message                              |
| `/summary`               | Returns total companies, avg revenue, growth |
| `/industry-distribution` | Returns count of companies by industry       |
| `/company/{name}`        | Detailed profile of a company (by name)      |
| `/top-growth`            | Top 5 companies with highest growth %        |

###  Example: /summary Output
{
  "total_companies": 35,
  "average_revenue": 12700000.0,
  "average_growth": 38.6
}

---

###  Output Files
- data/startups_raw.csv — Raw scraped data

- data/startups_clean.csv — Cleaned & formatted data

- visuals/*.png — Distribution plots

- visuals/summary.txt — Summary stats

---

###  Dependencies
See requirements.txt. Major packages:

pandas

matplotlib

seaborn

fastapi

uvicorn

beautifulsoup4

cloudscraper

---

###  Author
Prince Kumar

Department of CSE, IIT Jodhpur

---
###  License
This project is for academic/demo purposes only.

--