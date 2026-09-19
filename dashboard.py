import streamlit as st
import pandas as pd
import datetime
import os

# Set page configuration for a wider layout and modern look
st.set_page_config(
    page_title="Sutra Luminis Attendance", 
    page_icon="👑", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium aesthetic (Dark blue theme based on Sutra Luminis logo)
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* Top Header Styling */
    .main-header {
        color: #1a2533;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
        text-align: center;
        font-family: 'Georgia', serif;
        letter-spacing: 1px;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 40px;
        font-family: 'Helvetica', sans-serif;
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e5ec;
        padding: 20px 20px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #1a2533;
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    div[data-testid="metric-container"] > div {
        color: #1a2533;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a2533;
        color: white;
    }
    
    /* Headers in sidebar */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.02);
    }
    
    /* Hide index in tables */
    .row_heading.level0 {display:none}
    .blank {display:none}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Try to load logo if it exists, otherwise show stylized text
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.markdown("<h2 style='text-align: center; color: white; font-family: Georgia, serif; letter-spacing: 2px;'>👑<br>SUTRA LUMINIS<br><span style='font-size: 0.8rem; font-family: Helvetica; font-weight: normal; color: #a0aec0;'>Lighting & Decor</span></h2>", unsafe_allow_html=True)
    
    st.markdown("<br><hr style='border-color: #2d3748;'>", unsafe_allow_html=True)
    st.markdown("### 📤 Upload Report")
    uploaded_file = st.file_uploader("Select Excel, CSV, or PDF file", type=["csv", "xlsx", "xls", "pdf"])
    st.markdown("<hr style='border-color: #2d3748;'>", unsafe_allow_html=True)
    st.info("💡 **Pro Tip:** Save your logo image as `logo.png` in the same folder as this script to display it automatically at the top of this menu!")

# ================= MAIN CONTENT =================
st.markdown('<p class="main-header">Daily Attendance Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Monitor late arrivals and daily performance seamlessly.</p>', unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        with st.spinner("Analyzing biometric data..."):
            # Read the uploaded file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.pdf'):
                import pdfplumber
                all_data = []
                header = None
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            for row in table:
                                # Clean row of Nones and newlines
                                clean_row = [str(cell).replace('\\n', ' ').strip() if cell is not None else "" for cell in row]
                                # Check if this is the header row
                                if 'Empcode' in clean_row or 'Name' in clean_row:
                                    header = clean_row
                                elif header and any(clean_row): # Not empty row
                                    # Sometimes tables on next pages have headers again, skip them
                                    if 'Empcode' in clean_row:
                                        continue
                                    
                                    # Ensure the row has the same length as header
                                    if len(clean_row) == len(header):
                                        all_data.append(clean_row)
                                    elif len(clean_row) < len(header):
                                        all_data.append(clean_row + [""] * (len(header) - len(clean_row)))
                                    else:
                                        all_data.append(clean_row[:len(header)])
                
                if header and all_data:
                    df = pd.DataFrame(all_data, columns=header)
                else:
                    st.error("❌ **Error:** Could not extract tabular data from the PDF.")
                    df = pd.DataFrame()
            else:
                df = pd.read_excel(uploaded_file)
            
            if not df.empty:
                # Clean up column names (strip whitespace)
                df.columns = df.columns.str.strip()
                
                if 'INTime' not in df.columns:
                    st.error("❌ **Error:** Could not find the 'INTime' column in the uploaded file.")
                else:
                    # Clean the data
                    df_clean = df.copy()
                    df_clean['INTime'] = df_clean['INTime'].replace('--:--', pd.NA)
                    df_clean = df_clean.dropna(subset=['INTime'])
                    
                    # Parse INTime
                    df_clean['INTime_Parsed'] = pd.to_datetime(df_clean['INTime'], format='%H:%M', errors='coerce').dt.time
                    df_clean = df_clean.dropna(subset=['INTime_Parsed'])
                    
                    # Filter data
                    time_930 = datetime.time(9, 30)
                    time_945 = datetime.time(9, 45)
                    
                    after_930 = df_clean[df_clean['INTime_Parsed'] > time_930]
                    after_945 = df_clean[df_clean['INTime_Parsed'] > time_945]
                    
                    # --- Metrics ---
                    st.markdown("### 📊 Today's Overview")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(label="👥 Total Present", value=len(df_clean))
                    with col2:
                        st.metric(label="⚠️ Late (After 9:30 AM)", value=len(after_930))
                    with col3:
                        st.metric(label="🚨 Very Late (After 9:45 AM)", value=len(after_945))
                        
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    
                    # --- Detailed Reports ---
                    def get_display_columns(dataframe):
                        possible_cols = ['Empcode', 'Name', 'INTime', 'OUTTime', 'Status', 'Remark']
                        return [c for c in possible_cols if c in dataframe.columns]
    
                    st.markdown("### 📋 Detailed Reports")
                    tab1, tab2, tab3 = st.tabs(["⚠️ Arrived After 9:30 AM", "🚨 Arrived After 9:45 AM", "📄 View Raw Data"])
                    
                    with tab1:
                        if not after_930.empty:
                            cols_to_show = get_display_columns(after_930)
                            st.dataframe(after_930[cols_to_show].reset_index(drop=True), use_container_width=True, height=350)
                        else:
                            st.success("🎉 Excellent! No one arrived after 9:30 AM today.")
                            
                    with tab2:
                        if not after_945.empty:
                            cols_to_show = get_display_columns(after_945)
                            st.dataframe(after_945[cols_to_show].reset_index(drop=True), use_container_width=True, height=350)
                        else:
                            st.success("🎉 Excellent! No one arrived after 9:45 AM today.")
                            
                    with tab3:
                        st.dataframe(df, use_container_width=True, height=350)
                
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    # Empty state illustration
    st.markdown("<br><br>", unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.info("👈 **Welcome!** Please open the sidebar on the left and upload your daily report to see the analysis.")
