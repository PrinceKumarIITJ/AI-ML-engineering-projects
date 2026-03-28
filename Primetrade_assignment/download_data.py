import gdown
import os

def download_datasets():
    print("Downloading datasets...")
    os.makedirs("data", exist_ok=True)
    
    # Bitcoin Market Sentiment
    sentiment_id = "1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf"
    sentiment_output = "data/sentiment.csv"
    if not os.path.exists(sentiment_output):
        gdown.download(id=sentiment_id, output=sentiment_output, quiet=False)
        print(f"Downloaded {sentiment_output}")
    else:
        print(f"{sentiment_output} already exists.")
        
    # Historical Trader Data
    trader_data_id = "1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs"
    trader_output = "data/trader_data.csv"
    if not os.path.exists(trader_output):
        gdown.download(id=trader_data_id, output=trader_output, quiet=False)
        print(f"Downloaded {trader_output}")
    else:
        print(f"{trader_output} already exists.")

if __name__ == "__main__":
    download_datasets()
