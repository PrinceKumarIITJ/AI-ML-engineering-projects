import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from agent_insights import generate_insights, get_strategic_recommendation

# 🔧 App Configuration & Meta Settings
st.set_page_config(
    page_title="Luggage Intelligence PRO", 
    layout="wide", 
    page_icon="🧊",
    initial_sidebar_state="expanded"
)

# 🎨 Custom CSS for Neon, Glassmorphism & Advanced Dark Theme Aesthetics
st.markdown("""
<style>
    /* Global Typography Customizations */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Metric Card Customization */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #00FF9D; /* Neon Mint Accent */
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #8B9BB4 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Elegant Markdown Cards */
    .insight-card {
        padding: 20px;
        border-left: 4px solid #00FF9D;
        background: rgba(0, 255, 157, 0.05);
        border-radius: 8px;
        margin-bottom: 15px;
        font-size: 16px;
        color: #D1D5DB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s;
    }
    .insight-card:hover {
        transform: translateY(-2px);
    }
    
    .anomaly-card {
        padding: 18px;
        border-left: 4px solid #FF3A60;  /* Neon Red */
        background: rgba(255, 58, 96, 0.05);
        border-radius: 8px;
        margin-bottom: 15px;
        color: #F87171;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    .trust-card {
        padding: 18px;
        border-left: 4px solid #FBC02D;  /* Neon Yellow */
        background: rgba(251, 192, 45, 0.05);
        border-radius: 8px;
        margin-bottom: 15px;
        color: #FDE047;
    }

    /* Top Banner Styling */
    .top-banner {
        background: linear-gradient(90deg, #141E30 0%, #243B55 100%);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    h1 {
        font-weight: 700 !important;
        background: -webkit-linear-gradient(45deg, #00FF9D, #00B8FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2, h3 {
        color: #FFFFFF !important;
    }
    
    /* Clean up default Streamlit elements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        border-radius: 6px 6px 0 0;
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# 🔄 Data Loading Pipeline
@st.cache_data
def load_data():
    try:
        df_prod = pd.read_csv('data/processed_products.csv')
        df_rev = pd.read_csv('data/processed_reviews.csv')
        return df_prod, df_rev
    except FileNotFoundError:
        st.error("⚠️ Local Data missing! Please run the pipeline script.")
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_rev = load_data()

if df_prod.empty:
    st.stop()

# Clean missing numerical arrays to avoid plotly crashes
df_prod['Actual_Review_Count'] = df_prod['Actual_Review_Count'].fillna(1)
df_prod['Sentiment_Score_Avg'] = df_prod['Sentiment_Score_Avg'].fillna(0)

# 🎛️ Advanced Sidebar Engineering
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=60)
    st.title("Control Center")
    st.markdown("Use filters to live-update the executive dashboard.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Custom interactive widgets
    selected_brands = st.multiselect("🎯 Active Competitors", options=df_prod['Brand'].unique(), default=df_prod['Brand'].unique())
    st.markdown("<br>", unsafe_allow_html=True)
    
    price_range = st.slider("💰 Price Band (₹)", int(df_prod['Price'].min()), int(df_prod['Price'].max()), (int(df_prod['Price'].min()), int(df_prod['Price'].max())))
    st.markdown("<br>", unsafe_allow_html=True)
    
    min_rating = st.slider("⭐ Minimum Quality Star", 1.0, 5.0, 1.0, 0.1)
    
    st.markdown("---")
    st.markdown("<small style='color: #6B7280;'>Last Updated: Live NLP Engine</small>", unsafe_allow_html=True)

# 🚦 Apply Filters
df_filtered = df_prod[
    (df_prod['Brand'].isin(selected_brands)) &
    (df_prod['Price'] >= price_range[0]) &
    (df_prod['Price'] <= price_range[1]) &
    (df_prod['Rating'] >= min_rating)
]

# 📝 Top Banner
st.markdown("""
<div class="top-banner">
    <h1>Luggage Brand Intelligence PRO</h1>
    <span style="color: #9CA3AF; font-size: 1.1rem;">Automated Machine Learning Strategy Engine · Indian Market</span>
</div>
""", unsafe_allow_html=True)

# 🧭 Sleek Tab Navigation
tabs = st.tabs(["💡 AI Strategy Deck", "📊 Market Dynamics", "🛡️ Quality & Trust Anomalies", "🧬 Deep Product Profiler"])

# -------- TAB 1: AI Strategy Deck --------
with tabs[0]:
    st.subheader("High-Level KPIs")
    
    # Premium Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Analyzed SKUs", f"{len(df_filtered)} items")
    with m2:
        rev_count = len(df_rev[df_rev['Brand'].isin(selected_brands)])
        st.metric("Consumer Sentiments", f"{rev_count:,} reviews")
    with m3:
        st.metric("Avg Segment Price", f"₹{df_filtered['Price'].mean():.0f}", f"-{df_filtered['Discount_Pct'].mean():.1f}% avg discount", delta_color="inverse")
    with m4:
        st.metric("NLP Sentiment Base", f"{df_filtered['Sentiment_Score_Avg'].mean():.2f} / 1.0", "Baseline")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Dual Layout for Insights & Reccomendation
    insight_col, recco_col = st.columns([1.5, 1])
    
    with insight_col:
        st.markdown("### 🤖 Algorithmic Discoveries")
        insights = generate_insights(df_filtered)
        if not insights:
            st.info("No insights triggered for this specific slice of data.")
        for insight in insights:
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)
            
    with recco_col:
        st.markdown("### ⚡ C-Suite Action Plan")
        st.success(get_strategic_recommendation(df_filtered), icon="🎯")
        st.caption("AI-generated based on Aspect Sentiment and Trust Anomaly matrices.")


# -------- TAB 2: Market Dynamics --------
with tabs[1]:
    st.markdown("### Multidimensional Brand Benchmarking")
    
    col_viz1, col_viz2 = st.columns([1.2, 1])
    
    with col_viz1:
        # Improved Plotly Dark Theme Scatter
        fig_bubble = px.scatter(
            df_filtered, x="Price", y="Sentiment_Score_Avg", size="Actual_Review_Count", 
            color="Brand", hover_name="Title", size_max=45,
            color_discrete_sequence=['#00FF9D', '#00B8FF', '#FF3A60', '#FBC02D', '#9B51E0'],
            template="plotly_dark",
            title="Positioning Matrix: Price vs Perceived Quality (NLP)"
        )
        fig_bubble.add_hline(y=df_filtered['Sentiment_Score_Avg'].mean(), line_dash="solid", line_color="#374151")
        fig_bubble.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#D1D5DB')
        st.plotly_chart(fig_bubble, use_container_width=True)
        
    with col_viz2:
        # Advanced Spider Web Chart for Aspects
        st.markdown("<div style='text-align:center; font-weight:600; color:#E5E7EB; margin-bottom: 20px;'>Granular Component Sentiment (Radar)</div>", unsafe_allow_html=True)
        brand_asp = df_filtered.groupby('Brand')[['Aspect_wheels_Avg', 'Aspect_handle_Avg', 'Aspect_durability_Avg', 'Aspect_material_Avg', 'Aspect_zipper_Avg', 'Aspect_size_Avg']].mean().reset_index()
        fig_spider = go.Figure()
        categories = ['Wheels', 'Handles', 'Durability', 'Material', 'Zippers', 'Size']
        
        colors = ['#00FF9D', '#00B8FF', '#FF3A60', '#FBC02D', '#9B51E0']
        
        for index, row in brand_asp.iterrows():
            if row['Brand'] in selected_brands:
                fig_spider.add_trace(go.Scatterpolar(
                    r=[row['Aspect_wheels_Avg'], row['Aspect_handle_Avg'], row['Aspect_durability_Avg'], row['Aspect_material_Avg'], row['Aspect_zipper_Avg'], row['Aspect_size_Avg']],
                    theta=categories,
                    fill='toself',
                    name=row['Brand'],
                    line_color=colors[index % len(colors)],
                    opacity=0.7
                ))
        fig_spider.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[-0.5, 0.8], gridcolor='#374151'), bgcolor='rgba(0,0,0,0)'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            template='plotly_dark', font_color='#D1D5DB', margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_spider, use_container_width=True)

    st.markdown("---")
    
    # Margin vs Rating correlation
    fig_bar = px.scatter(
        df_filtered, x="Discount_Pct", y="Rating", color="Brand",
        color_discrete_sequence=['#00FF9D', '#00B8FF', '#FF3A60', '#FBC02D'],
        template="plotly_dark",
        title="Does Deep Discounting Cannibalize Perceived Quality? (Discount % vs Stars)"
    )
    fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#D1D5DB')
    st.plotly_chart(fig_bar, use_container_width=True)


# -------- TAB 3: Trust & Value Anomalies --------
with tabs[2]:
    st.markdown("### Risk Detection Engine")
    st.caption("Auto-flagging items where marketing metrics (Stars/Price) diverge heavily from NLP Ground Truth.")
    
    col_a1, col_a2 = st.columns([1, 1])
    
    with col_a1:
        st.markdown("#### 🚨 Hard Quality Warnings")
        anomalies = df_filtered[df_filtered['Product_Anomalies'] != "None"]
        if not anomalies.empty:
            for _, row in anomalies.iterrows():
                st.markdown(f"<div class='anomaly-card'><b>{row['Brand']}</b> - {row['Title']}<br><br><b>Tripped Wire:</b> {row['Product_Anomalies']}<br><br><small>Paper Rating: {row['Rating']} ⭐️ | Ground Truth Sentiment: {row['Sentiment_Score_Avg']:.2f}</small></div>", unsafe_allow_html=True)
        else:
            st.success("No critical quality anomalies detected in current filter state.")
            
    with col_a2:
        st.markdown("#### 🤖 Review Authenticity Flags")
        suspicious = pd.DataFrame(df_filtered.groupby('Brand')['Suspicious_Reviews_Count'].sum()).reset_index()
        fig_trust = px.bar(
            suspicious, x='Brand', y='Suspicious_Reviews_Count', 
            title="Suspicious NLP Patterns Detected (Bots/Duplicates)", 
            color='Brand',
            color_discrete_sequence=['#FF3A60', '#FBC02D', '#00FF9D', '#00B8FF'],
            template="plotly_dark"
        )
        fig_trust.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trust, use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### 🌟 Value-for-Money Normalization Quotient")
    st.caption("Evaluating product sentiment strictly against its peers in the same price tier. Ratio > 1.0 implies extraordinary market value.")
    
    df_sorted_vfm = df_filtered.sort_values(by="Value_Ratio", ascending=False)
    fig_vfm = px.bar(
        df_sorted_vfm.head(10), x="Value_Ratio", y="Title", color="Brand", orientation='h',
        color_discrete_sequence=['#00FF9D', '#00B8FF', '#FF3A60', '#FBC02D'],
        template="plotly_dark", height=450
    )
    fig_vfm.add_vline(x=1.0, line_dash="dash", line_color="#E5E7EB", annotation_text="Industry Baseline")
    fig_vfm.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_vfm, use_container_width=True)

# -------- TAB 4: Deep Product Profiler --------
with tabs[3]:
    st.markdown("### Surgical Product Drilldown")
    
    selected_product_title = st.selectbox("Select Target Product (SKU)", df_filtered['Title'].tolist())
    
    if selected_product_title:
        with st.expander(f"Data Profile: {selected_product_title}", expanded=True):
            prod_data = df_filtered[df_filtered['Title'] == selected_product_title].iloc[0]
            
            cp1, cp2, cp3 = st.columns(3)
            cp1.metric("Pricing Edge", f"₹{prod_data['Price']}", f"{prod_data['Discount_Pct']}% below MRP", delta_color="normal")
            cp2.metric("Public Stars", f"{prod_data['Rating']} ⭐️", f"{prod_data['Actual_Review_Count']} organic samples", delta_color="off")
            cp3.metric("True Sentiment Core", f"{prod_data['Sentiment_Score_Avg']:.2f}", f"VFM Ratio: {prod_data['Value_Ratio']:.2f}", delta_color="normal" if prod_data['Value_Ratio'] > 1 else "inverse")
            
            st.markdown("<br><b>Raw Verbatim Diagnostics</b>", unsafe_allow_html=True)
            revs_for_prod = df_rev[df_rev['Product_ID'] == prod_data['Product_ID']]
            
            # Show dataframe with premium styling
            st.dataframe(
                revs_for_prod[['Date', 'Rating', 'Review_Text', 'Sentiment_Score', 'Is_Suspicious', 'Suspicious_Reason']],
                use_container_width=True,
                height=300
            )
