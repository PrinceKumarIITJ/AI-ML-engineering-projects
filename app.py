"""
This file creates the visual Dashboard (User Interface) for the project.
It uses a library called 'Streamlit' to turn data from our database 
into a beautiful web page where managers can see live stats and download Excel reports.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from config import OUTPUT_DIR, TARGET_CITIES, DB_PATH
from models.database import DatabaseManager

# Premium Web App Config
st.set_page_config(page_title="IntelliLead | AI B2B Intelligence", layout="wide", page_icon="⚡")

# Custom UI Styles (Dynamic & Premium Aesthetic)
st.markdown("""
<style>
    /* Gradient Headings */
    h1 {
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Smooth Metrics Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(4px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 201, 255, 0.2);
        border: 1px solid rgba(0, 201, 255, 0.5);
    }
    
    /* Button Styling */
    .stDownloadButton button, .stButton button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #000 !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: transform 0.2s, opacity 0.2s;
    }
    .stDownloadButton button:hover, .stButton button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

db = DatabaseManager(DB_PATH)

st.title("⚡ IntelliLead Agent Platform")
st.markdown("**Automated Multi-Source Intelligence:** Eliminating duplicates, rejecting junk with NLP, and discovering missing verified data points across the digital footprint.")

st.sidebar.header("Agent Configuration")
cities = st.sidebar.multiselect("Active Target Geographies", TARGET_CITIES, default=["Jaipur", "Jodhpur", "Delhi"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚦 Orchestration")
if st.sidebar.button("▶ Trigger Pipeline Job"):
    st.sidebar.info("Execute via terminal using `python main.py` for long-running headless stability. This ensures Playwright correctly manipulates memory.")

# DB Stats 
st.markdown("### 📊 Live Database Insights")
try:
    total_raw = db.get_total_count()
    city_counts = db.get_city_counts()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total NLP-Approved Leads", f"{total_raw:,}")
    m2.metric("Active Regions", len(city_counts.keys()))
    m3.metric("Scraping Platforms", "6 Verified")
except Exception as e:
    st.warning("Database not initialized or empty. Run the scraping pipeline first.")

# Final Presentation & Reporting
st.markdown("---")
st.subheader("📑 Database & Reports")

# 1. Intelligence Discovery Feed (Live DB)
with st.expander("📡 Live Intelligence Discovery Feed", expanded=False):
    st.write("Last 10 leads identified by the Agentic Pipeline:")
    recent_leads = db.load_all_leads()[-10:] if total_raw > 0 else []
    if recent_leads:
        recent_df = pd.DataFrame([l.model_dump() for l in recent_leads])
        st.table(recent_df[['business_name', 'city', 'category', 'rating']].tail(10))
    else:
        st.info("No live feeds available yet.")

# 2. Multi-Report Comparative Viewer
all_reports = list(OUTPUT_DIR.glob("*.xlsx"))
if all_reports:
    report_names = [f.name for f in all_reports]
    master_file = "Wedding_Event_Companies_Master.xlsx"
    demo_file = "Demo_Leads_Report.xlsx"
    
    # Create Tabs for different views
    tab1, tab2 = st.tabs(["📊 Master Database (Historical)", "🧪 Quick Demo Results"])
    
    with tab1:
        if master_file in report_names:
            st.markdown(f"**Source:** `{master_file}`")
            xls_m = pd.ExcelFile(OUTPUT_DIR / master_file)
            s_m = st.selectbox("Sheet (Master)", xls_m.sheet_names, key="m_sheet")
            df_m = pd.read_excel(OUTPUT_DIR / master_file, sheet_name=s_m)
            
            # Numeric filtering/gradient logic
            n_cols_m = df_m.select_dtypes(include=['number']).columns
            g_cols_m = [c for c in df_m.columns if ('Score' in c or 'Rating' in c) and c in n_cols_m]
            st.dataframe(df_m.style.background_gradient(cmap="Blues", subset=g_cols_m) if g_cols_m else df_m, use_container_width=True, height=500)
            
            with open(OUTPUT_DIR / master_file, "rb") as f:
                st.download_button("⬇️ Download Master Excel", f, file_name=master_file)
        else:
            st.info("Master Database not found. Run the full pipeline to generate it.")

    with tab2:
        if demo_file in report_names:
            st.markdown(f"**Source:** `{demo_file}`")
            xls_d = pd.ExcelFile(OUTPUT_DIR / demo_file)
            s_d = st.selectbox("Sheet (Demo)", xls_d.sheet_names, key="d_sheet")
            df_d = pd.read_excel(OUTPUT_DIR / demo_file, sheet_name=s_d)
            
            n_cols_d = df_d.select_dtypes(include=['number']).columns
            g_cols_d = [c for c in df_d.columns if ('Score' in c or 'Rating' in c) and c in n_cols_d]
            st.dataframe(df_d.style.background_gradient(cmap="Greens", subset=g_cols_d) if g_cols_d else df_d, use_container_width=True, height=500)
            
            with open(OUTPUT_DIR / demo_file, "rb") as f:
                st.download_button("⬇️ Download Demo Report", f, file_name=demo_file)
        else:
            st.info("No Demo Report found. Run `python demo_run.py` to see live results here.")
else:
    st.info("No Excel reports generated yet.")

