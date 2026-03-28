import pandas as pd

def check_dates():
    sentiment = pd.read_csv('data/sentiment.csv')
    trader = pd.read_csv('data/trader_data.csv')

    print("--- Sentiment Dates ---")
    print(sentiment[['date', 'timestamp']].head())

    print("\n--- Trader Dates ---")
    print(trader[['Timestamp IST', 'Timestamp']].head())

if __name__ == "__main__":
    check_dates()
