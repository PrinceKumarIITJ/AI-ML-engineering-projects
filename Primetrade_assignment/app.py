import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Primetrade.ai Dashboard", layout="wide")

st.title("Primetrade.ai: Trader Performance vs Market Sentiment")

@st.cache_data
def load_data():
    df = pd.read_csv('data/daily_merged.csv')
    return df

df = load_data()

sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", ["All", "Fear", "Greed", "Neutral"])

display_df = df.copy()
def categorize_sentiment(c):
    c = str(c).lower()
    if 'fear' in c: return 'Fear'
    if 'greed' in c: return 'Greed'
    return 'Neutral'

display_df['Sentiment'] = display_df['classification'].apply(categorize_sentiment)

if sentiment_filter != "All":
    display_df = display_df[display_df['Sentiment'] == sentiment_filter]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Trades Analyzed", display_df['total_trades'].sum())
with col2:
    st.metric("Mean Daily PnL", f"${display_df['daily_pnl'].mean():.2f}")
with col3:
    st.metric("Average Win Rate", f"{display_df['win_rate'].mean():.2%}")

st.subheader("Performance Distribution")
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(display_df['daily_pnl'], bins=50, kde=True, ax=ax)
ax.set_xlim(-10000, 10000) # clip massive outliers for visualization
st.pyplot(fig)

st.subheader("Raw Data Sample")
st.dataframe(display_df.head(100))

if os.path.exists('bonus_insights.txt'):
    st.subheader("Bonus Machine Learning Insights")
    with open('bonus_insights.txt', 'r') as f:
        st.text(f.read())
