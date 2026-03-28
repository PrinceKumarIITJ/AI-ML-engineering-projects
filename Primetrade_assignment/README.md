# Primetrade.ai Data Science Intern Assignment: Trader Performance vs Market Sentiment

This repository contains the methodology, code, and findings for the Primetrade.ai analytical assignment.

## Setup and How to Run

1. **Environment Setup**
   Ensure you have Python 3 installed. It is recommended to use a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   *(Note: The required packages are `pandas`, `numpy`, `matplotlib`, `seaborn`, `gdown`.)*

2. **Execution Steps**
   The project is split into three modular scripts, plus bonus modules.
   
   **Core Analysis Pipeline:**
   - `python download_data.py`: Downloads the Bitcoin Market Sentiment and Trader Data from Google Drive into the `data/` folder.
   - `python analysis.py`: Parses timestamps, computes daily metrics (PnL, win rate, trade size, long/short ratio) for each account, aligns dates, and merges with the sentiment dataset into `data/daily_merged.csv`.
   - `python analysis_part_b.py`: Analyzes the merged data, compares Fear vs Greed states, creates trader segments, and generates visualizations in the `charts/` folder as well as an `insights.txt` report.

   **Bonus Modules:**
   - `python bonus_model.py`: Runs an unsupervised K-Means algorithm to cluster traders into Archetypes based on behavioral features. It also trains a Random Forest Classifier to predict next-day profitability based on sentiment and lagged performance metrics, saving findings to `bonus_insights.txt` and `data/trader_archetypes.csv`.
   - `streamlit run app.py`: Launches a lightweight, interactive web dashboard to explore the dataset, filter by Sentiment states, and view macro performance metrics dynamically.

## Methodology

**Data Preparation:** 
Datasets were loaded using Pandas. Timestamps in the Trader data (`Timestamp IST`) were parsed to a daily frequency (`date`). Daily trader metrics were aggregated (sum of PnL, count of trades, average USD size, Long vs Short count). Finally, an inner merge was performed on `date` with the Bitcoin Fear/Greed index. 

*(Note: "Leverage" was not explicitly provided as a column in the trader data, so `Size USD` was used as a proxy for aggressiveness/position sizing profile.)*

**Segmentation & Comparison:**
Traders were grouped by **Frequency** (above or below median trades per day) and **Size** (above or below median USD trade size). Performance was then grouped by "Fear" vs "Greed" sentiment labels to extract behavioral differences.

---

## Key Insights

1. **Performance Skewness on Fear Days:** 
   Mean PnL is higher on Fear days ($5,185) compared to Greed days ($4,144). However, the *Median PnL* is lower on Fear ($122) than on Greed ($265). This indicates that Fear days are driven by massive outlier tail-end wins (likely short squeezes or liquidation hunting), while Greed days produce steadier, more typical returns for the majority of the market. Win rates stay consistent across both at ~36%.

2. **Aggressive "Catch the Knife" Behavior:** 
   During Fear days, trader activity spikes dramatically. The average number of trades per day jumps from 76 (Greed) to 105 (Fear). The average trade size increases from $5,954 to $8,529. Most notably, the **Long/Short ratio surges from 14.5 to 45.5**, showing an overwhelming bias by traders attempting to long extreme dips.

3. **Frequent vs Infrequent Trader Disparity:**
   - **Frequent Traders** heavily outperform on Fear days ($5,968 avg PnL) versus Greed days ($3,846 avg PnL).
   - **Infrequent Traders** perform oppositely, underperforming significantly during Fear ($3,090 avg PnL) compared to their strong performance on Greed days ($4,987 avg PnL).

---

## Strategy Recommendations (Actionable Output)

Based on the statistical tendencies observed above, here are 2 proposed "rules of thumb" or strategy modifications:

**Rule 1: Sentiment-Based Scaling for Infrequent Traders**
*Insight:* Less active traders perform poorly during high-volatility "Fear" conditions and better during "Greed" trends.
*Action:* **Reduce position size or halt automated non-scalping strategies on Fear days for Infrequent/Trend-following traders.** Wait until the market transitions back to neutral or greedy regimes to resume normal scaling, as their standard edge is lost during choppy capitulation events.

**Rule 2: Volatility Harvesting for Active Traders**
*Insight:* Frequent traders thrive in "Fear" conditions by capturing massive tail-end outlier moves (mean PnL outpaces median drastically). Furthermore, the retail crowd is aggressively longing the dip (high L/S ratio).
*Action:* **Increase trade frequency and liquidity-providing algorithms for active traders during Fear days.** Focus strategies on fading the overwhelming Long bias (e.g., shorting into bounces), or sizing up cautiously to capture the heavy volatility and liquidations that are clearly padding the massive outlier profits of the active segment.
