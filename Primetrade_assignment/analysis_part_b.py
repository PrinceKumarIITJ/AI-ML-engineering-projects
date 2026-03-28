import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_analysis():
    os.makedirs('charts', exist_ok=True)
    df = pd.read_csv('data/daily_merged.csv')

    # Add broad sentiment category
    def categorize_sentiment(c):
        c = str(c).lower()
        if 'fear' in c: return 'Fear'
        if 'greed' in c: return 'Greed'
        return 'Neutral'
        
    df['sentiment_group'] = df['classification'].apply(categorize_sentiment)
    
    with open('insights.txt', 'w') as f:
        f.write("=== Primetrade.ai Trader Analysis vs Sentiment ===\n\n")

        # 1. Performance Differences (Fear vs Greed)
        perf = df.groupby('sentiment_group').agg(
            mean_pnl=('daily_pnl', 'mean'),
            median_pnl=('daily_pnl', 'median'),
            mean_win_rate=('win_rate', 'mean'),
            total_days=('date', 'nunique')
        )
        f.write("1. Performance Differences (Fear vs Greed)\n")
        f.write(perf.to_string() + "\n\n")

        # Visual 1: PnL by Sentiment
        plt.figure(figsize=(8, 6))
        sns.boxplot(data=df[df['sentiment_group'].isin(['Fear', 'Greed'])], x='sentiment_group', y='daily_pnl', showfliers=False)
        plt.title("Daily PnL Distribution: Fear vs Greed (Outliers Hidden)")
        plt.savefig('charts/pnl_by_sentiment.png')
        plt.close()

        # 2. Behavior Changes
        behav = df.groupby('sentiment_group').agg(
            avg_trades_per_day=('total_trades', 'mean'),
            avg_trade_size=('avg_trade_size_usd', 'mean'),
            avg_ls_ratio=('ls_ratio', 'mean')
        )
        f.write("2. Behavior Changes by Sentiment\n")
        f.write(behav.to_string() + "\n\n")
        
        # Visual 2: Trade Size by Sentiment
        plt.figure(figsize=(8, 6))
        sns.barplot(data=df[df['sentiment_group'].isin(['Fear', 'Greed'])], x='sentiment_group', y='avg_trade_size_usd')
        plt.title("Average Trade Size by Sentiment")
        plt.savefig('charts/trade_size_by_sentiment.png')
        plt.close()

        # 3. Trader Segments
        trader_profile = df.groupby('Account').agg(
            avg_size=('avg_trade_size_usd', 'mean'),
            total_trades=('total_trades', 'sum'),
            overall_win_rate=('win_rate', 'mean'),
            net_pnl=('daily_pnl', 'sum')
        )
        
        # Segment A: High Size vs Low Size (Proxy for Leverage)
        size_median = trader_profile['avg_size'].median()
        trader_profile['size_segment'] = np.where(trader_profile['avg_size'] > size_median, 'High Size', 'Low Size')
        
        # Segment B: Frequent vs Infrequent
        freq_median = trader_profile['total_trades'].median()
        trader_profile['freq_segment'] = np.where(trader_profile['total_trades'] > freq_median, 'Frequent', 'Infrequent')

        # Merge segments back to daily
        df = df.merge(trader_profile[['size_segment', 'freq_segment']], on='Account', how='left')

        # Performance of Frequent vs Infrequent on Fear/Greed days
        f.write("3. Segments Behavior on Fear vs Greed\n")
        seg_behav = df.groupby(['freq_segment', 'sentiment_group'])['daily_pnl'].mean().unstack()
        f.write(seg_behav.to_string() + "\n\n")

        # Visual 3: Frequency Segment Performance
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df[df['sentiment_group'].isin(['Fear', 'Greed'])], x='sentiment_group', y='daily_pnl', hue='freq_segment')
        plt.title("Mean Daily PnL by Sentiment and Trader Frequency")
        plt.savefig('charts/pnl_by_freq_and_sentiment.png')
        plt.close()
        
        print("Analysis complete! Insights written to insights.txt and charts saved in charts/")

if __name__ == "__main__":
    run_analysis()
