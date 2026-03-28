import pandas as pd
import numpy as np

def prep_data():
    print("Loading data...")
    sentiment = pd.read_csv('data/sentiment.csv')
    trader = pd.read_csv('data/trader_data.csv')
    
    sentiment['date'] = pd.to_datetime(sentiment['date'])
    trader['datetime'] = pd.to_datetime(trader['Timestamp IST'], dayfirst=True, errors='coerce')
    trader['date'] = trader['datetime'].dt.floor('D')
    
    trader['is_win'] = trader['Closed PnL'] > 0
    trader['is_loss'] = trader['Closed PnL'] < 0

    daily_trader_stats = trader.groupby(['Account', 'date']).agg(
        daily_pnl=('Closed PnL', 'sum'),
        total_trades=('Trade ID', 'count'),
        winning_trades=('is_win', 'sum'),
        losing_trades=('is_loss', 'sum'),
        avg_trade_size_usd=('Size USD', 'mean'),
        long_trades=('Direction', lambda x: x.astype(str).str.contains('Long').sum()),
        short_trades=('Direction', lambda x: x.astype(str).str.contains('Short').sum())
    ).reset_index()

    daily_trader_stats['win_rate'] = np.where(daily_trader_stats['total_trades'] > 0, 
                                              daily_trader_stats['winning_trades'] / daily_trader_stats['total_trades'], 
                                              0)
    daily_trader_stats['ls_ratio'] = np.where(daily_trader_stats['short_trades'] > 0, 
                                              daily_trader_stats['long_trades'] / daily_trader_stats['short_trades'], 
                                              daily_trader_stats['long_trades'])

    daily_merged = pd.merge(daily_trader_stats, sentiment[['date', 'classification', 'value']], on='date', how='inner')
    
    print("Sample Long/Short ratios:", daily_merged['ls_ratio'].head())
    print("\n--- Merged Data Head ---")
    print(daily_merged.head())
    
    daily_merged.to_csv('data/daily_merged.csv', index=False)
    
if __name__ == "__main__":
    prep_data()
