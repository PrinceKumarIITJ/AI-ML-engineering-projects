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

st.markdown("---")

# Final Presentation
excel_path = OUTPUT_DIR / "Wedding_Event_Companies_Master.xlsx"

st.subheader("📑 Final Processed & Enriched Output")
if excel_path.exists():
    try:
        xls = pd.ExcelFile(excel_path)
        
        # Action Bar
        col_btn, col_sheet, _ = st.columns([1, 1, 2])
        
        with col_sheet:
            sheet = st.selectbox("View Regional Database", xls.sheet_names)
            
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            with open(excel_path, "rb") as file:
                btn = st.download_button(
                        label="⬇️ Download Master Excel",
                        data=file,
                        file_name="Wedding_Event_Companies_Master.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        df = pd.read_excel(excel_path, sheet_name=sheet)
        
        # Display
        st.dataframe(
            df.style.background_gradient(cmap="Blues", subset=[c for c in df.columns if 'Score' in c or 'Rating' in c]),
            use_container_width=True, 
            height=600
        )
        
    except Exception as e:
        st.error(f"Error reading intelligence output: {e}")
else:
    st.info("No Master Excel file generated yet. Please run `python main.py` to initiate the multi-platform intelligence gathering process.")

