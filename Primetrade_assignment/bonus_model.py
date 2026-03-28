import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def run_bonus_tasks():
    df = pd.read_csv('data/daily_merged.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['Account', 'date'])

    # === TASK 1: Clustering Traders into Behavioral Archetypes ===
    # Aggregate trader behavior over the whole period
    trader_profile = df.groupby('Account').agg(
        total_pnl=('daily_pnl', 'sum'),
        avg_trade_size=('avg_trade_size_usd', 'mean'),
        total_trades=('total_trades', 'sum'),
        avg_win_rate=('win_rate', 'mean')
    ).fillna(0)

    # Scale and cluster
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(trader_profile)
    kmeans = KMeans(n_clusters=3, random_state=42)
    trader_profile['Cluster'] = kmeans.fit_predict(scaled_features)

    # Map clusters to descriptive archetype names based on centroids
    centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=trader_profile.columns[:-1])
    # Just generic labels for simplicity
    cluster_labels = {0: 'Archetype A', 1: 'Archetype B', 2: 'Archetype C'}
    trader_profile['Archetype'] = trader_profile['Cluster'].map(cluster_labels)
    trader_profile.to_csv('data/trader_archetypes.csv')

    # === TASK 2: Predictive Model for Next-Day Profitability ===
    # Create lag features
    df['prev_pnl'] = df.groupby('Account')['daily_pnl'].shift(1)
    df['prev_win_rate'] = df.groupby('Account')['win_rate'].shift(1)
    df['prev_trades'] = df.groupby('Account')['total_trades'].shift(1)
    df['prev_sentiment_val'] = df.groupby('Account')['value'].shift(1)
    
    # Target: is today profitable?
    df['target_is_profitable'] = (df['daily_pnl'] > 0).astype(int)

    # Drop NaNs resulted from shifting
    model_df = df.dropna(subset=['prev_pnl', 'prev_win_rate', 'prev_trades', 'prev_sentiment_val', 'target_is_profitable'])

    features = ['prev_pnl', 'prev_win_rate', 'prev_trades', 'prev_sentiment_val', 'value'] # using today's sentiment and yesterday's performance
    X = model_df[features]
    y = model_df['target_is_profitable']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X_train, y_train)
    preds = rf.predict(X_test)

    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds)

    with open('bonus_insights.txt', 'w') as f:
        f.write("=== BONUS: Trader Archetypes (Clustering) ===\n")
        f.write(str(trader_profile.groupby('Archetype').mean()) + "\n\n")
        f.write("=== BONUS: Next-Day Profitability Prediction ===\n")
        f.write(f"Model: Random Forest Classifier\n")
        f.write(f"Accuracy: {acc:.2f}\n")
        f.write("Classification Report:\n")
        f.write(report + "\n")
        f.write(f"Feature Importances:\n")
        for name, imp in zip(features, rf.feature_importances_):
            f.write(f" - {name}: {imp:.4f}\n")

    print("Bonus modeling complete! Check bonus_insights.txt for results.")

if __name__ == "__main__":
    run_bonus_tasks()
