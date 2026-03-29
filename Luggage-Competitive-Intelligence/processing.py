import pandas as pd
import numpy as np
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re
from collections import Counter
import nltk

# Auto-download punkt tokenizers for TextBlob
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Initialize VADER
analyzer = SentimentIntensityAnalyzer()

# Define aspects and their keywords
ASPECT_KEYWORDS = {
    'wheels': ['wheel', 'roller', 'glide', 'spinner', 'castor'],
    'handle': ['handle', 'grip', 'telescopic', 'trolley'],
    'material': ['material', 'shell', 'plastic', 'fabric', 'scratch', 'polycarbonate'],
    'zipper': ['zip', 'zipper', 'teeth', 'lock'],
    'size': ['size', 'space', 'capacity', 'spacious', 'bulky', 'cabin', 'fit'],
    'durability': ['durability', 'durable', 'sturdy', 'broke', 'crack', 'long lasting', 'tough']
}

def clean_data(products_path, reviews_path):
    # Load data
    try:
        df_prod = pd.read_csv(products_path)
        df_rev = pd.read_csv(reviews_path)
    except FileNotFoundError:
        print("Raw data not found. Please run mock_data_generator.py first.")
        return None, None
        
    # Drop NAs
    df_prod = df_prod.dropna(subset=['Product_ID', 'Title', 'Price'])
    df_rev = df_rev.dropna(subset=['Review_Text', 'Rating'])
    
    # Ensure types
    df_prod['Price'] = df_prod['Price'].astype(float)
    df_rev['Rating'] = df_rev['Rating'].astype(float)
    
    return df_prod, df_rev

def get_vader_sentiment(text):
    if not isinstance(text, str):
        return 0.0
    return analyzer.polarity_scores(text)['compound']

def extract_aspect_sentiments(text):
    if not isinstance(text, str):
        return {}
        
    sentences = TextBlob(text).sentences
    aspect_scores = {}
    
    for aspect, keywords in ASPECT_KEYWORDS.items():
        scores = []
        for sentence in sentences:
            sentence_str = str(sentence).lower()
            if any(keyword in sentence_str for keyword in keywords):
                # Score just this sentence with VADER
                scores.append(analyzer.polarity_scores(sentence_str)['compound'])
        if scores:
             # Average sentiment for this aspect in this review
             aspect_scores[aspect] = sum(scores) / len(scores)
             
    return aspect_scores

def process_reviews(df_rev):
    print("Processing reviews (NLP, Sentiment, Aspects)...")
    
    # Overall Sentiment
    df_rev['Sentiment_Score'] = df_rev['Review_Text'].apply(get_vader_sentiment)
    
    # Extract aspect scores column (dict)
    df_rev['Aspects'] = df_rev['Review_Text'].apply(extract_aspect_sentiments)
    
    # Flatten aspects into individual columns
    for aspect in ASPECT_KEYWORDS.keys():
        df_rev[f'Aspect_{aspect}'] = df_rev['Aspects'].apply(lambda x: x.get(aspect, np.nan))
        
    # Detect Suspicious Trust Signals
    # Signal 1: Repeated identical text by different users/same brand (indicates bots or fake reviews)
    text_counts = df_rev['Review_Text'].value_counts()
    suspicious_texts = text_counts[text_counts > 1].index.tolist()
    
    def flag_suspicious(row):
        is_suspicious = False
        reasons = []
        # Repetition
        if row['Review_Text'] in suspicious_texts:
            is_suspicious = True
            reasons.append("Duplicate Review Text")
        # Extreme polarity mismatch: 5 star but highly negative text
        if row['Rating'] == 5 and row['Sentiment_Score'] < -0.3:
            is_suspicious = True
            reasons.append("High Rating vs Negative Text")
        return pd.Series({'Is_Suspicious': is_suspicious, 'Suspicious_Reason': " | ".join(reasons)})
        
    trust_flags = df_rev.apply(flag_suspicious, axis=1)
    df_rev = pd.concat([df_rev, trust_flags], axis=1)
    
    return df_rev

def process_products(df_prod, df_rev):
    print("Aggregating metrics to product level...")
    
    # Aggregate review data per product
    agg_funcs = {
        'Rating': ['mean', 'count'],
        'Sentiment_Score': 'mean',
        'Is_Suspicious': 'sum'
    }
    
    # Add aspect aggregations
    for aspect in ASPECT_KEYWORDS.keys():
         agg_funcs[f'Aspect_{aspect}'] = 'mean'
         
    rev_agg = df_rev.groupby('Product_ID').agg(agg_funcs).reset_index()
    # Flatten columns
    rev_agg.columns = ['_'.join(col).strip('_').replace('_mean', '_Avg') for col in rev_agg.columns.values]
    rev_agg.rename(columns={'Rating_count': 'Actual_Review_Count', 'Is_Suspicious_sum': 'Suspicious_Reviews_Count'}, inplace=True)
    
    # Merge with products
    df_final = pd.merge(df_prod, rev_agg, on='Product_ID', how='left')
    
    # Value for Money Normalization
    print("Calculating Value-for-Money Metrics...")
    
    # Create price tiers
    df_final['Price_Tier'] = pd.qcut(df_final['Price'], q=3, labels=['Budget', 'Mid-Range', 'Premium'])
    
    # Calculate baseline average sentiment per tier
    tier_baselines = df_final.groupby('Price_Tier', observed=False)['Sentiment_Score_Avg'].transform('mean')
    
    # Calculate Value Ratio: Ratio of actual sentiment to expected sentiment for that price tier
    # Handling divide by zero or negative baselines carefully
    df_final['Value_Ratio'] = df_final['Sentiment_Score_Avg'] / (tier_baselines.replace({0:0.01}))
    df_final['Value_Ratio'] = df_final['Value_Ratio'].fillna(1.0)
    
    # Anomaly Detection at Product Level
    # e.g., High official product rating but terrible NLP sentiment score or high durability complaints
    def detect_product_anomalies(row):
        anomalies = []
        if pd.notnull(row['Sentiment_Score_Avg']):
             if row['Rating'] >= 4.0 and row['Sentiment_Score_Avg'] < 0.2:
                 anomalies.append("Overrated (Poor Sentiment)")
             
             if pd.notnull(row.get('Aspect_durability_Avg')) and row['Aspect_durability_Avg'] < 0 and row['Rating'] >= 4.0:
                 anomalies.append("Repeated Durability Complaints despite High Rating")
                 
        return " | ".join(anomalies) if anomalies else "None"
        
    df_final['Product_Anomalies'] = df_final.apply(detect_product_anomalies, axis=1)
    
    return df_final

if __name__ == "__main__":
    prod_path = "data/raw_products.csv"
    rev_path = "data/raw_reviews.csv"
    
    df_prod, df_rev = clean_data(prod_path, rev_path)
    
    if df_prod is not None:
        processed_reviews = process_reviews(df_rev)
        processed_reviews.to_csv("data/processed_reviews.csv", index=False)
        
        final_dataset = process_products(df_prod, processed_reviews)
        final_dataset.to_csv("data/processed_products.csv", index=False)
        print("Processing complete. Saved to data/processed_products.csv and data/processed_reviews.csv")
