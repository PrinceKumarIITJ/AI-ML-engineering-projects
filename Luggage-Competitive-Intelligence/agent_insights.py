import pandas as pd
import numpy as np

def generate_insights(df_prod):
    """Generates automated strategic insights based on summarized data logic."""
    insights = []
    
    # Pre-compute aggregates
    brand_agg = df_prod.groupby('Brand').agg({
        'Price': 'mean',
        'Discount_Pct': 'mean',
        'Rating': 'mean',
        'Sentiment_Score_Avg': 'mean',
        'Value_Ratio': 'mean',
        'Aspect_durability_Avg': 'mean',
        'Suspicious_Reviews_Count': 'sum'
    }).reset_index()
    
    # 1. Winning Brand by Sentiment vs Price (Value Proposition)
    best_value = brand_agg.loc[brand_agg['Value_Ratio'].idxmax()]
    insights.append(f"🏆 **Value Leader**: {best_value['Brand']} shows the strongest value proposition. Despite an average price of ₹{int(best_value['Price'])}, it maintains a sentiment score ({best_value['Sentiment_Score_Avg']:.2f}) that outperforms expectations for its price tier.")

    # 2. The Discount Dependency Trap
    highest_discount = brand_agg.loc[brand_agg['Discount_Pct'].idxmax()]
    if highest_discount['Sentiment_Score_Avg'] < brand_agg['Sentiment_Score_Avg'].mean():
        insights.append(f"📉 **Margin Risk**: {highest_discount['Brand']} relies on deep discounts (Avg {highest_discount['Discount_Pct']}% off MRP) to drive sales, but fails to convert this into customer satisfaction (Below average sentiment). This indicates a brand perception issue where low price is mistaken for low quality.")

    # 3. Durability Anomaly (High Rating vs Broken Wheels/Handles)
    # Using the aspect-level sentiment for durability
    lowest_durability = brand_agg.loc[brand_agg['Aspect_durability_Avg'].idxmin()]
    if pd.notnull(lowest_durability['Aspect_durability_Avg']) and lowest_durability['Rating'] >= 4.0:
        insights.append(f"⚠️ **Hidden Churn Risk**: {lowest_durability['Brand']} maintains a high 4.0+ average star rating, but its NLP-extracted durability sentiment is the lowest in the segment ({lowest_durability['Aspect_durability_Avg']:.2f}). Decision makers should investigate raw material QA immediately, as star ratings may be lagging indicators of recent manufacturing defects.")

    # 4. Premium Positioning Validation
    premium_brands = df_prod[df_prod['Price_Tier'] == 'Premium']
    if not premium_brands.empty:
        premium_leader = premium_brands.groupby('Brand')['Sentiment_Score_Avg'].mean().idxmax()
        insights.append(f"✨ **Premium Dominance**: In the premium segment, {premium_leader} defends its price point successfully. Customer sentiment justifies the premium, showing that buyers are willing to pay more when fundamental aspects (wheels, zippers) feel sturdy.")
        
    # 5. Trust and Suspicious Reviews Signal
    most_suspicious = brand_agg.loc[brand_agg['Suspicious_Reviews_Count'].idxmax()]
    if most_suspicious['Suspicious_Reviews_Count'] > 5:
        insights.append(f"🕵️ **Review Integrity Alert**: {most_suspicious['Brand']} exhibits the highest count of suspicious reviews (duplicated text or massive rating/sentiment mismatches). Analyzing organic review volume vs incentivized reviews is recommended to understand true baseline demand.")

    return insights
    
def get_strategic_recommendation(df_prod):
    """Provides a final conclusive recommendation block for the decision maker."""
    brand_sentiments = df_prod.groupby('Brand')['Sentiment_Score_Avg'].mean()
    top_brand = brand_sentiments.idxmax()
    
    bottom_brand = brand_sentiments.idxmin()
    
    recco = (
        f"**Immediate Action Plan:**\n"
        f"1. **Adopt {top_brand}'s Playbook**: {top_brand} is winning not just on price, but on consistent positive sentiment across essential components (wheels, handles). Study their component sourcing.\n"
        f"2. **Intervene on {bottom_brand}:** {bottom_brand} requires a turnaround strategy. Before adjusting pricing, fix the core product flaws isolated in the aspect-sentiment drilldown.\n"
        f"3. **Review Quality over Quantity**: A high volume of reviews paired with negative NLP sentiment signals strong awareness but poor retention. Focus marketing spend entirely on verified-quality products."
    )
    return recco

if __name__ == "__main__":
    df = pd.read_csv("data/processed_products.csv")
    insights = generate_insights(df)
    for i in insights:
        print(i)
    
    print("\nStrategic Recommendation:")
    print(get_strategic_recommendation(df))
