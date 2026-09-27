import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:5000"

# Force sidebar to be expanded by default so navigation is never hidden
st.set_page_config(
    page_title="HealthChain AI | Clinical EHR Platform",
    page_icon="ΓÜò∩╕Å",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PREMIMUM DESIGN SYSTEM (LINEAR / STRIPE AESTHETIC)
# Single typography family: Plus Jakarta Sans
# Curated Palette: Deep Slate #0F172A, Royal Blue #2563EB, Crisp Light #F8FAFC
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300..700;1,9..40,300..700&family=Lato:wght@300;400;700&display=swap');

    /* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
       WARM LIGHT DESIGN TOKENS
       Palette: cream bg ┬╖ warm white cards ┬╖ sky blue
       accent ┬╖ earth brown text ┬╖ soft borders
       ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */
    :root {
        --bg:          #F7F4F0;
        --surface:     #FFFFFF;
        --surface-2:   #FAF8F5;
        --sidebar-bg:  #F2EDE6;
        --accent:      #4A90B8;
        --accent-h:    #3A7FA6;
        --accent-lt:   #E8F4FA;
        --accent-ring: rgba(74,144,184,.18);
        --border:      #E4DDD5;
        --border-2:    #D0C8BE;
        --t1:  #2C2218;
        --t2:  #6B5B52;
        --t3:  #A89387;
        --low:      #2563EB;
        --moderate: #D97706;
        --high:     #DC2626;
        --neutral:  #A89387;
        --r-lg: 16px;
        --r-md: 10px;
        --r-sm:  7px;
        --s-xs: 0 1px 2px rgba(44,34,24,.05);
        --s-sm: 0 1px 4px rgba(44,34,24,.07), 0 1px 2px rgba(44,34,24,.04);
        --s-md: 0 4px 14px rgba(44,34,24,.09), 0 2px 4px rgba(44,34,24,.05);
        --s-lg: 0 12px 36px rgba(44,34,24,.12), 0 4px 10px rgba(44,34,24,.06);
    }

    html, body, * { font-family: 'DM Sans','Lato',system-ui,sans-serif !important; -webkit-font-smoothing: antialiased; box-sizing: border-box; }
    .stApp { background: var(--bg) !important; }
    .block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px !important; }

    h1,h2,h3,h4,h5,h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-family: 'DM Sans',sans-serif !important;
        color: var(--t1) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* body text */
    section.main p,
    section.main li,
    section.main label,
    [data-testid="stMarkdownContainer"] p { color: var(--t2) !important; font-size: 0.91rem !important; line-height: 1.65 !important; }
    section.main h1,section.main h2,section.main h3,section.main h4 { color: var(--t1) !important; }
    [data-testid="stCaptionContainer"] p,.stCaption p { color: var(--t3) !important; font-size: 0.81rem !important; }
    [data-testid="stAlert"] p,[data-testid="stAlert"] span { color: var(--t1) !important; font-size: 0.88rem !important; }
    #MainMenu,footer,header { visibility: hidden !important; }
    .stDeployButton,[data-testid="stStatusWidget"] { display: none !important; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] { background: var(--sidebar-bg) !important; border-right: 1px solid var(--border) !important; }
    section[data-testid="stSidebar"] * { color: var(--t1) !important; font-family: 'DM Sans',sans-serif !important; }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--t3) !important; font-size: 0.7rem !important; font-weight: 700 !important; letter-spacing: 0.09em !important; text-transform: uppercase !important; }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span { color: var(--t2) !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] { display: flex !important; flex-direction: column !important; gap: 2px !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label { color: var(--t2) !important; font-size: 0.88rem !important; font-weight: 500 !important; padding: 9px 14px !important; border-radius: var(--r-sm) !important; transition: background 0.12s,color 0.12s !important; cursor: pointer !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(74,144,184,.10) !important; color: var(--accent) !important; }
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] .stButton button { background: #DC2626 !important; border: none !important; color: #FFFFFF !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.87rem !important; padding: 0.55rem 1rem !important; width: 100% !important; margin-top: 1.5rem !important; box-shadow: none !important; transition: background 0.15s !important; }
    section[data-testid="stSidebar"] button:hover { background: #B91C1C !important; transform: none !important; }

    /* INPUTS */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea { background: var(--surface) !important; border: 1.5px solid var(--border) !important; border-radius: var(--r-sm) !important; color: var(--t1) !important; font-size: 0.9rem !important; padding: 0.55rem 0.85rem !important; box-shadow: var(--s-xs) !important; transition: border-color 0.15s,box-shadow 0.15s !important; }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-ring) !important; outline: none !important; }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder { color: var(--t3) !important; }
    .stNumberInput button { background: transparent !important; border: 1px solid var(--border) !important; color: var(--t2) !important; border-radius: 5px !important; padding: 0 !important; margin-top: 0 !important; width: 28px !important; min-width: 28px !important; box-shadow: none !important; }
    .stNumberInput button:hover { background: var(--bg) !important; border-color: var(--border-2) !important; transform: none !important; box-shadow: none !important; }
    [data-baseweb="select"] > div:first-child { background: var(--surface) !important; border: 1.5px solid var(--border) !important; border-radius: var(--r-sm) !important; color: var(--t1) !important; font-size: 0.9rem !important; box-shadow: var(--s-xs) !important; }
    [data-baseweb="select"] > div:first-child:hover { border-color: var(--border-2) !important; }
    [data-baseweb="popover"] ul { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important; box-shadow: var(--s-md) !important; }
    [data-baseweb="popover"] li { color: var(--t1) !important; font-size: 0.88rem !important; }
    [data-baseweb="popover"] li:hover { background: var(--accent-lt) !important; color: var(--accent) !important; }
    [data-testid="stFileUploader"] { background: var(--surface) !important; border: 1.5px dashed var(--border) !important; border-radius: var(--r-md) !important; padding: 1.25rem !important; transition: border-color 0.15s !important; }
    [data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }
    [data-testid="stFileUploader"] p,[data-testid="stFileUploader"] span,[data-testid="stFileUploader"] small { color: var(--t2) !important; font-size: 0.88rem !important; }
    [data-testid="stFileUploader"] button { background: var(--accent-lt) !important; color: var(--accent) !important; border: 1px solid #BEE0F0 !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.82rem !important; padding: 0.35rem 0.9rem !important; margin-top: 0 !important; width: auto !important; box-shadow: none !important; }
    [data-testid="stFileUploader"] button:hover { background: #D6EEF8 !important; transform: none !important; box-shadow: none !important; }

    /* SLIDER */
    [data-testid="stSlider"] > div > div > div { background: var(--border) !important; }
    [data-testid="stSlider"] [role="slider"] { background: var(--accent) !important; border: 2px solid #FFFFFF !important; box-shadow: var(--s-sm),0 0 0 2px var(--accent) !important; width: 18px !important; height: 18px !important; }
    [data-testid="stSlider"] > div > div > div > div { background: var(--accent) !important; }
    [data-testid="stSlider"] [data-testid="stTickBarMin"],[data-testid="stSlider"] [data-testid="stTickBarMax"] { color: var(--t3) !important; font-size: 0.78rem !important; }

    /* BUTTONS */
    [data-testid="stFormSubmitButton"] button,button[kind="primary"] { background: var(--accent) !important; color: #FFFFFF !important; border: none !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.9rem !important; padding: 0.58rem 1.4rem !important; box-shadow: 0 1px 3px rgba(74,144,184,.30) !important; transition: background 0.15s,box-shadow 0.15s,transform 0.1s !important; cursor: pointer !important; }
    [data-testid="stFormSubmitButton"] button:hover,button[kind="primary"]:hover { background: var(--accent-h) !important; box-shadow: 0 4px 14px rgba(74,144,184,.38) !important; transform: translateY(-1px) !important; }
    [data-testid="stFormSubmitButton"] button:active,button[kind="primary"]:active { transform: translateY(0) !important; }
    button[kind="secondary"],.stButton > button[kind="secondary"] { background: var(--surface) !important; color: var(--t1) !important; border: 1.5px solid var(--border) !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.88rem !important; padding: 0.52rem 1.1rem !important; box-shadow: var(--s-xs) !important; transition: border-color 0.15s,box-shadow 0.15s,transform 0.1s !important; }
    button[kind="secondary"]:hover,.stButton > button[kind="secondary"]:hover { border-color: var(--border-2) !important; box-shadow: var(--s-sm) !important; transform: translateY(-1px) !important; }
    [data-testid="stDownloadButton"] button { background: var(--accent-lt) !important; color: var(--accent) !important; border: 1px solid #BEE0F0 !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.84rem !important; padding: 0.42rem 1rem !important; box-shadow: none !important; margin-top: 0 !important; transition: background 0.15s !important; }
    [data-testid="stDownloadButton"] button:hover { background: #D6EEF8 !important; transform: none !important; box-shadow: none !important; }

    /* DATAFRAME */
    [data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--r-md) !important; overflow: hidden !important; box-shadow: var(--s-xs) !important; }
    [data-testid="stDataFrame"] th { background: var(--surface-2) !important; color: var(--t2) !important; font-size: 0.74rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; border-bottom: 1px solid var(--border) !important; padding: 10px 14px !important; }
    [data-testid="stDataFrame"] td { color: var(--t1) !important; font-size: 0.875rem !important; padding: 9px 14px !important; border-bottom: 1px solid var(--border) !important; }
    [data-testid="stDataFrame"] tr:hover td { background: var(--accent-lt) !important; }
    [data-testid="stSpinner"] > div { border-top-color: var(--accent) !important; }
    [data-testid="stProgressBar"] > div { background: var(--accent) !important; border-radius: 99px !important; }

    /* CARDS */
    .flat-card,.card { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--r-md) !important; padding: 1.4rem 1.6rem !important; box-shadow: var(--s-sm) !important; margin-bottom: 1.1rem !important; transition: box-shadow 0.18s,transform 0.18s !important; }
    .flat-card:hover,.card:hover { box-shadow: var(--s-md) !important; transform: translateY(-1px) !important; }

    /* METRIC CARDS */
    .metric-container { display: grid; grid-template-columns: repeat(auto-fit,minmax(210px,1fr)); gap: 1rem; margin-bottom: 1.75rem; }
    .metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); padding: 1.3rem 1.5rem; box-shadow: var(--s-sm); display: flex; flex-direction: column; gap: 0.25rem; transition: box-shadow 0.15s,transform 0.15s; }
    .metric-card:hover { box-shadow: var(--s-md); transform: translateY(-2px); }
    .metric-card-label { font-size: 0.69rem; text-transform: uppercase; letter-spacing: 0.09em; color: var(--t3); font-weight: 700; }
    .metric-card-value { font-size: 1.85rem; font-weight: 700; color: var(--t1); letter-spacing: -0.03em; }
    .metric-card-footer { font-size: 0.76rem; color: var(--t2); font-weight: 400; }

    /* BADGES */
    .badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 5px; font-size: 0.69rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; }
    .badge-low      { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .badge-moderate { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .badge-high     { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
    .badge-na,.badge-info { background: var(--surface-2); color: var(--t3); border: 1px solid var(--border); }

    /* HASH BADGE */
    .hash-badge { display: inline-block; background: var(--surface-2); color: var(--t2); border: 1px solid var(--border); border-radius: 5px; padding: 2px 7px; font-family: 'SF Mono','Fira Code',Consolas,monospace !important; font-size: 0.78rem; font-weight: 600; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; vertical-align: middle; cursor: default; transition: background 0.12s; }
    .hash-badge:hover { background: var(--border); }
    code { background: var(--surface-2) !important; color: var(--t2) !important; border: 1px solid var(--border) !important; border-radius: 5px !important; padding: 2px 7px !important; font-family: 'SF Mono','Fira Code',Consolas,monospace !important; font-size: 0.82em !important; }

    /* TIMELINE */
    .timeline-track { position: relative; margin-left: 10px; padding-left: 28px; border-left: 2px solid var(--border); padding-bottom: 1.25rem; }
    .timeline-dot   { position: absolute; left: -7px; top: 20px; width: 12px; height: 12px; border-radius: 50%; background: var(--surface); z-index: 2; }
    .timeline-dot-low      { border: 3px solid var(--low) !important;      box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important; }
    .timeline-dot-moderate { border: 3px solid var(--moderate) !important;  box-shadow: 0 0 0 3px rgba(217,119,6,.12) !important; }
    .timeline-dot-high     { border: 3px solid var(--high) !important;      box-shadow: 0 0 0 3px rgba(220,38,38,.12) !important; }
    .timeline-dot-na       { border: 3px solid var(--neutral) !important;   box-shadow: 0 0 0 3px rgba(168,147,135,.12) !important; }
    .timeline-card-low      { border-left: 3px solid var(--low) !important; }
    .timeline-card-moderate { border-left: 3px solid var(--moderate) !important; }
    .timeline-card-high     { border-left: 3px solid var(--high) !important; }
    .timeline-card-na       { border-left: 3px solid var(--neutral) !important; }

    /* AUTH */
    .auth-wrap { background: linear-gradient(135deg,#EEE8E0 0%,#F7F4F0 60%); border-radius: 18px; border: 1px solid var(--border); padding: 2.25rem 1.75rem; box-shadow: var(--s-xs); }
    .brand-panel { background: linear-gradient(155deg,#2C2218 0%,#4A3828 60%,#3A5068 100%); border-radius: 14px; padding: 3rem 2.75rem; min-height: 440px; display: flex; flex-direction: column; justify-content: center; position: relative; overflow: hidden; box-shadow: var(--s-lg); }
    .brand-panel::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 85% 15%,rgba(74,144,184,.22) 0%,transparent 55%); pointer-events: none; }
    .brand-title { font-size: 2rem !important; font-weight: 700 !important; color: #F7F4F0 !important; letter-spacing: -0.03em !important; margin: 0 !important; }
    .brand-sub   { font-size: 0.73rem !important; font-weight: 600 !important; color: #7DBDD8 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin: 6px 0 0 !important; }
    .brand-rule  { width: 36px; height: 2.5px; background: var(--accent); border-radius: 99px; margin: 1.2rem 0; }
    .brand-desc  { font-size: 0.86rem !important; color: #B8A898 !important; line-height: 1.65 !important; margin-bottom: 1.5rem !important; }
    .brand-feat  { display: flex; align-items: center; gap: 11px; font-size: 0.85rem; color: #D0C4B8; font-weight: 400; margin-bottom: 0.9rem; }
    .auth-card { background: var(--surface); border: 1px solid var(--border); border-top: 3px solid var(--accent); border-radius: var(--r-md); padding: 2rem 2rem 2.25rem; box-shadow: var(--s-sm); max-width: 440px; margin: 0 auto; }
    [data-testid="stAlert"][data-baseweb="notification"] { border-radius: var(--r-sm) !important; border-left-width: 3px !important; font-size: 0.88rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def trigger_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

def format_hash_badge(hash_str, prefix_len=8, suffix_len=4):
    """Format an EHR ID or IPFS CID badge with truncation and full hover title tooltip."""
    if not hash_str or str(hash_str).strip() in ["N/A", "None", ""]:
        return "<span class='hash-badge' title='Not Available'>N/A</span>"
    
    clean_str = str(hash_str).strip()
    if len(clean_str) <= (prefix_len + suffix_len + 3):
        display_str = clean_str
    else:
        display_str = f"{clean_str[:prefix_len]}...{clean_str[-suffix_len:]}"
        
    return f"<span class='hash-badge' title='{clean_str}'>{display_str}</span>"

def parse_blockchain_prediction(prediction_str):
    """Safely parse the prediction metadata stored in the blockchain ledger."""
    if not prediction_str:
        return {
            "prediction": "Not Evaluated",
            "risk_score": 0.0,
            "risk_level": "N/A",
            "timestamp": "N/A",
            "doctor_id": "N/A",
            "doctor_notes": "No observations recorded.",
            "type": "manual"
        }
        
    if isinstance(prediction_str, dict):
        if "prediction" in prediction_str:
            return prediction_str
        return {
            "prediction": prediction_str.get("prediction", "Not Evaluated"),
            "risk_score": float(prediction_str.get("risk_score", 0.0)),
            "risk_level": prediction_str.get("risk_level", "N/A"),
            "timestamp": prediction_str.get("timestamp", "N/A"),
            "doctor_id": prediction_str.get("doctor_id", "N/A"),
            "doctor_notes": prediction_str.get("doctor_notes", "No observations recorded."),
            "type": prediction_str.get("type", "manual")
        }

    try:
        data = json.loads(prediction_str)
        if isinstance(data, dict):
            if "prediction" not in data:
                data["prediction"] = "Not Evaluated"
            return data
    except Exception:
        pass
    
    # Fallback structure for old or manually created records
    pred_val = str(prediction_str)
    return {
        "prediction": pred_val,
        "risk_score": 0.0,
        "risk_level": "N/A" if pred_val == "Not Evaluated" else "Low Risk",
        "timestamp": "N/A",
        "doctor_id": "N/A",
        "doctor_notes": "No observations recorded.",
        "type": "manual"
    }

def sort_records_chronologically(records, reverse=False):
    """Sort a list of ledger records chronologically by their internal prediction timestamp."""
    def get_record_timestamp(rec):
        pred = parse_blockchain_prediction(rec.get("mlPrediction"))
        ts_str = pred.get("timestamp", "")
        if ts_str and ts_str != "N/A":
            try:
                clean_ts = ts_str.replace(" UTC", "")
                return datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        return datetime.min
    return sorted(records, key=get_record_timestamp, reverse=reverse)

# ==========================================
# AUTH PORTAL (LOGIN / REGISTER)
# ==========================================

if 'token' not in st.session_state:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    col_brand, col_form = st.columns([1.25, 1], gap="large")
    
    with col_brand:
        st.markdown("""
        <div class="brand-panel">
            <div style="margin-bottom: 1.35rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h5v5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/></svg>
            </div>
            <p class="brand-title">HealthChain AI</p>
            <p class="brand-sub">Decentralized Electronic Health Records</p>
            <div class="brand-rule"></div>
            <p class="brand-desc">
                Enterprise-grade clinical EHR powered by Scikit-Learn ML,
                Hyperledger Fabric smart contracts, and IPFS distributed storage.
            </p>
            <div style="margin-top: 0.5rem;">
                <div class="brand-feat">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                    Patient-controlled permissions via Smart Contracts
                </div>
                <div class="brand-feat">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                    Automated Gradient Boosting predictive analysis
                </div>
                <div class="brand-feat">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" x2="12" y1="22.08" y2="12"/></svg>
                    Immutable medical file hosting on IPFS node networks
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_form:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        # Segmented Control Tab Switcher inside the card header
        tab_login_col, tab_signup_col = st.columns(2)
        with tab_login_col:
            is_login = st.session_state.auth_mode == "login"
            if st.button("Log In", key="segmented_login", type="primary" if is_login else "secondary", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
        with tab_signup_col:
            is_signup = st.session_state.auth_mode == "register"
            if st.button("Sign Up", key="segmented_signup", type="primary" if is_signup else "secondary", use_container_width=True):
                st.session_state.auth_mode = "register"
                st.rerun()

        st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

        # Display registration success message if redirected
        if 'reg_success' in st.session_state:
            st.success(st.session_state.reg_success)
            del st.session_state.reg_success

        if st.session_state.auth_mode == "login":
            st.markdown("""
            <div style="text-align: left; margin-bottom: 1.25rem;">
                <h2 style="margin: 0; color: #0F172A; font-size: 1.45rem; font-family:'Plus Jakarta Sans'; font-weight: 800; letter-spacing:-0.03em;">Portal Access</h2>
                <p style="color: #64748B; font-size: 0.85rem; margin-top:3px;">Log in to authenticate your node keys on the network</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username Identifier", placeholder="e.g. doctor_smith")
                password = st.text_input("Security Key / Password", type="password", placeholder="ΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇó")
                login_submit = st.form_submit_button("Authenticate Identity ΓåÆ", type="primary", use_container_width=True)
                
            if login_submit:
                if not username or not password:
                    st.error("Missing login credentials.")
                else:
                    with st.spinner("Verifying ledger credentials..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state.token = data['token']
                                st.session_state.role = data['role']
                                st.session_state.username = data['username']
                                st.rerun()
                            else:
                                st.error(res.json().get('message', 'Authentication failed.'))
                        except Exception as e:
                            st.error(f"Failed to connect to Flask API server. {e}")

        else:
            st.markdown("""
            <div style="text-align: left; margin-bottom: 1.25rem;">
                <h2 style="margin: 0; color: #0F172A; font-size: 1.45rem; font-family:'Plus Jakarta Sans'; font-weight: 800; letter-spacing:-0.03em;">Node Registration</h2>
                <p style="color: #64748B; font-size: 0.85rem; margin-top:3px;">Register a new participant on the network</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("register_form"):
                new_username = st.text_input("Choose Username Identifier", placeholder="e.g. patient_doe")
                new_password = st.text_input("Choose Secure Password", type="password")
                role = st.selectbox("Assign System Role", ["patient", "doctor", "admin"])
                register_submit = st.form_submit_button("Create Identity Ledger Key ΓåÆ", type="primary", use_container_width=True)
                
            if register_submit:
                if not new_username or not new_password:
                    st.error("Fields cannot be empty.")
                else:
                    with st.spinner("Registering node identity..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/register",
                                                json={"username": new_username, "password": new_password, "role": role})
                            if res.status_code == 201:
                                # Save success state and redirect to login
                                st.session_state.reg_success = f"Γ£à Node identity '{new_username}' registered successfully! Please log in."
                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error(res.json().get('message', 'Registration rejected.'))
                        except Exception as e:
                            st.error(f"Failed to connect to Flask API server. {e}")

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ==========================================
# MAIN NAVIGATION (Replaced Sidebar)
# ==========================================

col_nav1, col_nav2 = st.columns([8, 2], vertical_alignment="bottom")

with col_nav1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h5v5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/></svg>
        <h3 style="color: #2C2218; margin: 0; font-size: 1.4rem; font-family:'DM Sans'; font-weight:800;">HealthChain AI</h3>
        <div style="display:inline-block; background: #E8F4FA; border: 1px solid #BEE0F0; color: #3A7FA6; border-radius: 999px; padding: 3px 12px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; font-family:'DM Sans';">
            {st.session_state.role} ΓÇó ≡ƒæñ {st.session_state.username.capitalize()}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.role == "patient":
        page = st.radio(
            "Navigation",
            ["Dashboard Overview", "Upload Medical File", "Access Delegation"],
            horizontal=True,
            label_visibility="collapsed"
        )
    elif st.session_state.role == "doctor":
        page = st.radio(
            "Navigation",
            ["Shared Records", "AI Clinical Assistant"],
            horizontal=True,
            label_visibility="collapsed"
        )
    elif st.session_state.role == "admin":
        page = st.radio(
            "Navigation",
            ["Dashboard Summary", "User Directory", "Network Diagnostics"],
            horizontal=True,
            label_visibility="collapsed"
        )

with col_nav2:
    if st.button("≡ƒÜ¬ Log Out", use_container_width=True):
        trigger_logout()

st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 2rem; border-color: var(--border);'>", unsafe_allow_html=True)


# ==========================================
# PATIENT PAGES
# ==========================================

if st.session_state.role == "patient":
    
    # ΓöÇΓöÇ Patient Dashboard Overview
    if "Dashboard Overview" in page:
        st.title("Patient EHR Dashboard")
        st.caption("Access your health history, medical scans, and automated AI health reports.")
        
        # Load Patient Records
        records = []
        with st.spinner("Syncing data with Hyperledger Fabric..."):
            try:
                res = requests.get(f"{API_BASE_URL}/get_my_records", headers=api_headers())
                if res.status_code == 200:
                    records = sort_records_chronologically(res.json())
            except Exception as e:
                st.error(f"Ledger connection failed: {e}")
                
        # Stats summary
        total_recs = len(records)
        ai_recs = sum(1 for r in records if parse_blockchain_prediction(r.get("mlPrediction")).get("type") == "prediction")
        recent_diag = "No Diagnosis Yet"
        recent_risk = "N/A"
        
        if records:
            last_record = records[-1]
            last_pred = parse_blockchain_prediction(last_record.get("mlPrediction"))
            recent_diag = last_pred.get("prediction", "Healthy")
            recent_risk = last_pred.get("risk_level", "N/A")
            
        # Metric Cards Layout
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-card-label">Secured Health Records</div>
                <div class="metric-card-value">{total_recs}</div>
                <div class="metric-card-footer">Anchored in Fabric blockchain</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">AI Diagnostic Reports</div>
                <div class="metric-card-value">{ai_recs}</div>
                <div class="metric-card-footer">Calculated by local Gradient Boosting model</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Recent Diagnosis</div>
                <div class="metric-card-value" style="font-size:1.5rem;">{recent_diag}</div>
                <div class="metric-card-footer">Risk Level: <b>{recent_risk}</b></div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Ledger Security</div>
                <div class="metric-card-value" style="color:#10B981;">ACTIVE</div>
                <div class="metric-card-footer">Double Endorsed Node Network</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Lucide ClipboardList SVG Header
        st.markdown("""
        <div style="display:flex; align-items:center; margin-bottom: 1.25rem; margin-top: 1.75rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4A90B8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/></svg>
            <h3 style="margin:0; color:#2C2218; font-family:'DM Sans'; font-size:1.35rem; font-weight:700;">Your Health Record Timeline</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not records:
            st.info("No records are linked to your identity. Upload a medical document or consult a doctor to generate AI prediction records.")
        else:
            for idx, rec in enumerate(reversed(records)):
                rec_id = rec.get("id")
                ipfs_hash = rec.get("ipfsHash")
                pred_meta = parse_blockchain_prediction(rec.get("mlPrediction"))
                
                # Determine risk level badge & 4-state indicator styling
                rl = str(pred_meta.get("risk_level")).lower()
                if "high" in rl:
                    badge_class = "badge-high"
                    timeline_card_class = "timeline-card-high"
                    timeline_dot_class = "timeline-dot-high"
                elif "mod" in rl:
                    badge_class = "badge-moderate"
                    timeline_card_class = "timeline-card-moderate"
                    timeline_dot_class = "timeline-dot-moderate"
                elif "low" in rl:
                    badge_class = "badge-low"
                    timeline_card_class = "timeline-card-low"
                    timeline_dot_class = "timeline-dot-low"
                else:
                    # Neutral 4th fallback state for N/A or Not Evaluated records
                    badge_class = "badge-na"
                    timeline_card_class = "timeline-card-na"
                    timeline_dot_class = "timeline-dot-na"
                    
                st.markdown(f"""
                <div class="timeline-track">
                    <div class="timeline-dot {timeline_dot_class}"></div>
                    <div class="flat-card {timeline_card_class}" style="margin-bottom:0px;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
                            <div>
                                <h4 style="margin:0 0 4px 0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-weight:700; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
                                    EHR ID: {format_hash_badge(rec_id)}
                                </h4>
                                <p style="margin:2px 0; font-size:0.82rem; color:#64748B;">Uploaded: {pred_meta.get('timestamp', 'N/A')}</p>
                            </div>
                            <span class="badge {badge_class}">{pred_meta.get('prediction')} ┬╖ {pred_meta.get('risk_level')}</span>
                        </div>
                        <div style="margin-top: 10px; font-size: 0.88rem; color:#334155; line-height: 1.55;">
                            <strong>Doctor Observations:</strong> {pred_meta.get('doctor_notes', 'N/A')}
                        </div>
                        <div style="margin-top: 8px; font-size: 0.78rem; color:#64748B; display:flex; align-items:center; gap:6px;">
                            <span>IPFS Hash (CID):</span> {format_hash_badge(ipfs_hash, 10, 6)}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render action buttons below the timeline card
                col_space, col_btn = st.columns([1, 15])
                with col_btn:
                    if pred_meta.get("type") == "prediction":
                        try:
                            pdf_res = requests.get(f"{API_BASE_URL}/download_report/{rec_id}", headers=api_headers())
                            if pdf_res.status_code == 200:
                                st.download_button(
                                    label="≡ƒôÑ Clinical PDF Report",
                                    data=pdf_res.content,
                                    file_name=f"clinical_report_{rec_id}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_patient_{rec_id}"
                                )
                        except Exception:
                            st.caption("PDF unavailable")
                    else:
                        ipfs_gateway = f"http://127.0.0.1:8080/ipfs/{ipfs_hash}"
                        st.markdown(f"[≡ƒöù View Document]({ipfs_gateway})")
                st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)
                
    # ΓöÇΓöÇ Patient Upload File
    elif "Upload Medical File" in page:
        st.title("Upload Medical Records")
        st.caption("Securely upload clinical documents, PDFs, or lab reports to decentralized IPFS and Fabric.")
        
        col_x, col_y = st.columns([5, 3], gap="large")
        with col_x:
            st.markdown('<div class="flat-card">', unsafe_allow_html=True)
            with st.form("manual_upload_form", clear_on_submit=True):
                p_id = st.text_input("Patient ID", value=st.session_state.username, disabled=True)
                doc_prediction = st.text_input("Record Label / Description (Optional)", placeholder="e.g. Cardiovascular Diagnostic Scan")
                uploaded_file = st.file_uploader("Select Clinical Document (PDF/Image/TXT)", type=["pdf", "png", "jpg", "jpeg", "txt"])
                submit_file = st.form_submit_button("Store & Inscribe Record ΓåÆ", type="primary", use_container_width=True)
                
            if submit_file:
                if not uploaded_file:
                    st.error("Please upload a file first.")
                else:
                    with st.spinner("Uploading to IPFS and anchoring blockchain metadata..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
                            data = {"patient_id": p_id, "prediction": doc_prediction or "Manual Upload"}
                            res = requests.post(f"{API_BASE_URL}/upload_record", files=files, data=data, headers=api_headers())
                            
                            if res.status_code == 200:
                                res_data = res.json()
                                st.success("Γ£à File securely stored on IPFS & Blockchain!")
                                st.markdown(f"**EHR Record ID:** {format_hash_badge(res_data.get('record_id'))}", unsafe_allow_html=True)
                                st.markdown(f"**IPFS CID:** {format_hash_badge(res_data.get('ipfs_hash'), 10, 6)}", unsafe_allow_html=True)
                                st.info("This file is private. Only you can access it until you explicitly authorize a clinician.")
                            else:
                                st.error(f"Transaction failed: {res.text}")
                        except Exception as e:
                            st.error(f"Network error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_y:
            st.markdown("""
            <div class="flat-card" style="background:#E8F4FA; border-left:4px solid #4A90B8;">
                <div style="display:flex; align-items:center; margin-bottom: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4A90B8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                    <h4 style="margin:0; color:#2C2218; font-family:'DM Sans'; font-weight:700;">Decoupled Storage Flow</h4>
                </div>
                <p style="font-size:0.875rem; color:#6B5B52; line-height:1.6; margin:0;">
                    Raw medical documents are saved onto <strong>IPFS (InterPlanetary File System)</strong>. 
                    IPFS hashes (CIDs) are immutable. This CID, combined with your Patient ID, is written onto the 
                    <strong>Hyperledger Fabric Smart Contract</strong>. 
                    No raw files are stored on-ledger, ensuring perfect privacy and high performance.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ΓöÇΓöÇ Patient Access Control Page
    elif "Access Delegation" in page:
        st.title("Access Delegation Control")
        st.caption("You control your privacy. Delegate viewing authorization to clinics and doctors on the network.")
        
        # Load Patient's Records for selection
        records = []
        try:
            res = requests.get(f"{API_BASE_URL}/get_my_records", headers=api_headers())
            if res.status_code == 200:
                records = res.json()
        except Exception as e:
            st.error(f"Failed to fetch records: {e}")
            
        col_x, col_y = st.columns([5, 4], gap="large")
        with col_x:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom:1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z"/><path d="m9 12 2 2 4-4"/></svg>
                <h4 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.15rem; font-weight:700;">Delegate Access</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if not records:
                st.info("No records found on the ledger. Upload a record before granting access.")
            else:
                record_options = {f"EHR ID: {r.get('id')} ΓÇö Label: {parse_blockchain_prediction(r.get('mlPrediction')).get('prediction')}": r.get('id') for r in records}
                
                st.markdown('<div class="flat-card">', unsafe_allow_html=True)
                with st.form("grant_access_form"):
                    selected_label = st.selectbox("Choose Medical Record", list(record_options.keys()))
                    doctor_username = st.text_input("Enter Doctor's Username", placeholder="e.g. dr_smith")
                    submit_grant = st.form_submit_button("Grant Ledger Access Keys ΓåÆ", type="primary", use_container_width=True)
                    
                if submit_grant:
                    record_id = record_options[selected_label]
                    if not doctor_username:
                        st.error("Please enter a doctor's username.")
                    else:
                        with st.spinner("Updating smart contract ledger access lists..."):
                            try:
                                res = requests.post(f"{API_BASE_URL}/grant_access",
                                                    json={"record_id": record_id, "doctor_id": doctor_username},
                                                    headers=api_headers())
                                if res.status_code == 200:
                                    st.success(f"Γ£à Immutable access granted successfully to Dr. {doctor_username}!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to grant access: {res.text}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
                
        with col_y:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom:1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                <h4 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.15rem; font-weight:700;">Ledger Access Lists</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if not records:
                st.caption("No authorizations to display.")
            else:
                for rec in records:
                    st.markdown(f"""
                    <div class="flat-card" style="padding:1rem 1.25rem; margin-bottom:10px;">
                        <div style="font-weight:700; color:#0F172A; font-size:0.9rem; font-family:'Plus Jakarta Sans'; display:flex; align-items:center; gap:6px;">
                            <span>Record ID:</span> {format_hash_badge(rec.get('id'))}
                        </div>
                        <div style="font-size:0.8rem; color:#64748B; margin-top:6px;">
                            <strong>Authorized Nodes:</strong> {", ".join(rec.get('authorizedUsers', []))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# ==========================================
# DOCTOR PAGES
# ==========================================

elif st.session_state.role == "doctor":
    
    # ΓöÇΓöÇ Doctor Dashboard: Shared Records
    if "Shared Records" in page:
        st.title("Patient Medical Directory")
        st.caption("Access all clinical data and health predictions explicitly shared with your clinical identity.")
        
        # Load Records Shared with Doctor
        records = []
        with st.spinner("Querying secure Hyperledger Fabric ledger..."):
            try:
                res = requests.get(f"{API_BASE_URL}/get_records_by_doctor", headers=api_headers())
                if res.status_code == 200:
                    records = sort_records_chronologically(res.json())
            except Exception as e:
                st.error(f"Ledger connection failed: {e}")
                
        if not records:
            st.info("≡ƒô¡ No patient records have been shared with your clinician account yet.")
        else:
            # Search, Filter, Sort Controls
            st.markdown('<div class="flat-card" style="padding:1rem 1.25rem;">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([4, 3, 3, 2])
            
            with col1:
                search_query = st.text_input("≡ƒöì Search Patients", placeholder="Enter Patient ID...").strip()
            with col2:
                record_types = ["All Types", "AI Prediction Reports", "Manual Uploads"]
                type_filter = st.selectbox("≡ƒôü Document Type", record_types)
            with col3:
                conditions = ["All Conditions", "Healthy", "Arthritis", "Asthma", "Cancer", "Diabetes", "Hypertension", "Obesity"]
                cond_filter = st.selectbox("≡ƒº¼ Diagnostic Filter", conditions)
            with col4:
                sort_order = st.selectbox("ΓÅ│ Sort Date", ["Newest First", "Oldest First"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Filter Logic
            filtered_records = []
            for r in records:
                p_id = str(r.get("patientId", "")).lower()
                if search_query and search_query.lower() not in p_id:
                    continue
                    
                pred_meta = parse_blockchain_prediction(r.get("mlPrediction"))
                
                rec_type = pred_meta.get("type", "manual")
                if type_filter == "AI Prediction Reports" and rec_type != "prediction":
                    continue
                if type_filter == "Manual Uploads" and rec_type != "manual":
                    continue
                    
                diag = pred_meta.get("prediction", "")
                if cond_filter != "All Conditions" and cond_filter != diag:
                    continue
                    
                filtered_records.append((r, pred_meta))
                
            if sort_order == "Newest First":
                filtered_records.reverse()
                
            st.markdown(f"Showing **{len(filtered_records)}** matching records out of **{len(records)}** total shared documents.")
            
            for rec, pred_meta in filtered_records:
                rec_id = rec.get("id")
                patient_id = rec.get("patientId")
                ipfs_hash = rec.get("ipfsHash")
                
                rl = str(pred_meta.get("risk_level")).lower()
                if "high" in rl:
                    badge_class = "badge-high"
                    card_border = "#EF4444"
                elif "mod" in rl:
                    badge_class = "badge-moderate"
                    card_border = "#F59E0B"
                elif "low" in rl:
                    badge_class = "badge-low"
                    card_border = "#2563EB"
                else:
                    badge_class = "badge-na"
                    card_border = "#94A3B8"
                    
                st.markdown(f"""
                <div class="flat-card" style="border-left: 4px solid {card_border};">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; border-bottom: 1px solid #F1F5F9; padding-bottom:8px; margin-bottom:10px;">
                        <div>
                            <h4 style="margin:0 0 4px 0; font-size:1.15rem; color:#0F172A; font-family:'Plus Jakarta Sans'; font-weight:700; display:flex; align-items:center; gap:8px;">
                                EHR Record: {format_hash_badge(rec_id)}
                            </h4>
                            <span style="font-size:0.8rem; color:#64748B;">Patient: <b>{patient_id.upper()}</b> | Date: {pred_meta.get('timestamp', 'N/A')}</span>
                        </div>
                        <span class="badge {badge_class}">{pred_meta.get('prediction')} ┬╖ {pred_meta.get('risk_level')}</span>
                    </div>
                    <div style="font-size: 0.875rem; color:#334155; margin-bottom:10px; line-height: 1.5;">
                        <strong>Physician Notes:</strong> {pred_meta.get('doctor_notes', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                
                if pred_meta.get('type') == 'manual':
                    st.markdown(f"<div style='margin-bottom: 8px;'><span style='background-color:#FEF3C7; color:#D97706; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>Pending Evaluation</span> <span style='font-size: 0.75rem; color: #64748B;'>Copy the EHR ID above and use the AI Clinical Assistant to evaluate this record.</span></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="font-size: 0.78rem; color:#64748B; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
                        <span>IPFS Content Identifier (CID):</span> {format_hash_badge(ipfs_hash, 10, 6)}
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 3, 4])
                with col1:
                    if pred_meta.get("type") == "prediction":
                        try:
                            pdf_res = requests.get(f"{API_BASE_URL}/download_report/{rec_id}", headers=api_headers())
                            if pdf_res.status_code == 200:
                                st.download_button(
                                    label="≡ƒôÑ Download Clinical PDF",
                                    data=pdf_res.content,
                                    file_name=f"clinical_report_{rec_id}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_dr_{rec_id}"
                                )
                        except Exception:
                            st.caption("PDF unavailable")
                    else:
                        st.caption("Manual upload PDF")
                with col2:
                    ipfs_gateway = f"http://127.0.0.1:8080/ipfs/{ipfs_hash}"
                    st.markdown(f"[≡ƒöù View Document on IPFS]({ipfs_gateway})")
                st.markdown("</div>", unsafe_allow_html=True)

    # ΓöÇΓöÇ Doctor Dashboard: AI Clinical Assistant (Prediction Form)
    elif "AI Clinical Assistant" in page:
        st.title("Clinical AI Diagnostic Assistant")
        st.caption("Enter patient physiological metrics and lifestyles to perform classification diagnostics.")
        
        if 'last_prediction' not in st.session_state:
            st.session_state.last_prediction = None
            st.session_state.patient_vitals = None
            
        col_x, col_y = st.columns([7, 5], gap="large")
        
        with col_x:
            st.subheader("Patient Vitals Input Form")
            st.markdown('<div class="flat-card">', unsafe_allow_html=True)
            with st.form("prediction_input_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    age = st.number_input("Age (Years)", 1, 120, 45)
                    gender = st.selectbox("Biological Gender", ["Male", "Female"])
                    glucose = st.number_input("Fasting Glucose Level (mg/dL)", 40, 400, 100)
                    bp = st.number_input("Systolic Blood Pressure (mm Hg)", 60, 260, 120)
                    bmi = st.number_input("Body Mass Index (BMI)", 10.0, 65.0, 24.5, format="%.2f")
                    oxygen = st.number_input("Oxygen Saturation Level (%)", 70.0, 100.0, 98.2, format="%.1f")
                    stay = st.number_input("Hospital Length of Stay (Days)", 0, 90, 3)
                    chol = st.number_input("Total Serum Cholesterol (mg/dL)", 80, 500, 190)
                    trig = st.number_input("Triglycerides Level (mg/dL)", 30, 800, 150)
                with col_b:
                    hba1c = st.number_input("HbA1c Level (%)", 3.0, 18.0, 5.4, format="%.2f")
                    smoking = st.selectbox("Current Tobacco Smoker?", ["No", "Yes"])
                    alcohol = st.selectbox("Frequent Alcohol Consumer?", ["No", "Yes"])
                    active_hours = st.slider("Weekly Physical Activity (Hours)", 0.0, 25.0, 4.5, 0.5)
                    diet_score = st.slider("Dietary Score (0 = Poor, 10 = Ideal)", 0.0, 10.0, 6.5, 0.5)
                    fam_history = st.selectbox("Family History of Disease?", ["No", "Yes"])
                    stress = st.slider("Subjective Stress Level (0 - 10)", 0.0, 10.0, 4.0, 0.5)
                    sleep = st.slider("Daily Sleep Hours", 0.0, 12.0, 7.5, 0.5)
                    
                st.markdown("<br/>", unsafe_allow_html=True)
                run_btn = st.form_submit_button("Run Diagnostics & Analysis ΓåÆ", type="primary", use_container_width=True)
                
            if run_btn:
                vitals = {
                    "Age": age,
                    "Gender": gender,
                    "Glucose": glucose,
                    "Blood Pressure": bp,
                    "BMI": bmi,
                    "Oxygen Saturation": oxygen,
                    "LengthOfStay": stay,
                    "Cholesterol": chol,
                    "Triglycerides": trig,
                    "HbA1c": hba1c,
                    "Smoking": 1 if smoking == "Yes" else 0,
                    "Alcohol": 1 if alcohol == "Yes" else 0,
                    "Physical Activity": active_hours,
                    "Diet Score": diet_score,
                    "Family History": 1 if fam_history == "Yes" else 0,
                    "Stress Level": stress,
                    "Sleep Hours": sleep
                }
                
                with st.spinner("Analysing clinical data via Gradient Boosting Classifier..."):
                    try:
                        res = requests.post(f"{API_BASE_URL}/predict", json={"vitals": vitals}, headers=api_headers())
                        if res.status_code == 200:
                            st.session_state.last_prediction = res.json()
                            st.session_state.patient_vitals = vitals
                            st.success("Γ£à Diagnostic analysis complete! Review findings on the panel.")
                        else:
                            st.error(f"Model error: {res.text}")
                    except Exception as e:
                        st.error(f"Cannot communicate with model endpoint: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_y:
            st.subheader("Diagnostic Results Panel")
            if not st.session_state.last_prediction:
                st.info("Fill out the vitals form and click Run Diagnostics to view predictions.")
            else:
                pred_res = st.session_state.last_prediction
                vitals = st.session_state.patient_vitals
                
                rl = str(pred_res.get("risk_level")).lower()
                badge_class = "badge-low"
                card_border = "#2563EB"
                if "high" in rl:
                    badge_class = "badge-high"
                    card_border = "#EF4444"
                elif "mod" in rl:
                    badge_class = "badge-moderate"
                    card_border = "#F59E0B"
                elif "low" in rl:
                    badge_class = "badge-low"
                    card_border = "#2563EB"
                else:
                    badge_class = "badge-na"
                    card_border = "#94A3B8"
                    
                st.markdown(f"""
                <div class="flat-card" style="border-top: 4px solid {card_border};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase; font-family:'Plus Jakarta Sans';">AI Diagnostic Assessment</span>
                        <span class="badge {badge_class}">{pred_res.get('risk_level')} Risk</span>
                    </div>
                    <div style="font-size:2rem; font-weight:800; color:#0F172A; margin: 10px 0 5px; font-family:'Plus Jakarta Sans'; letter-spacing:-0.03em;">
                        {pred_res.get('prediction')}
                    </div>
                    <div style="font-size:0.875rem; color:#475569;">
                        Model Confidence Score: <b>{pred_res.get('confidence_score'):.2%}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### ≡ƒôè Condition Probability Distributions")
                probs = pred_res.get("probabilities", {})
                if probs:
                    df_probs = pd.DataFrame({
                        "Condition": list(probs.keys()),
                        "Probability": [val * 100 for val in probs.values()]
                    }).sort_values(by="Probability", ascending=True)
                    st.bar_chart(df_probs.set_index("Condition"), horizontal=True)
                    
                st.markdown("""
                <div style="display:flex; align-items:center; margin-bottom: 0.75rem; margin-top: 1rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                    <h5 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.05rem; font-weight:700;">Preventive Clinical Advisories</h5>
                </div>
                """, unsafe_allow_html=True)
                
                recs = pred_res.get("recommendations", [])
                for r in recs:
                    st.markdown(f"- <span style='font-size:0.88rem; color:#334155;'>{r}</span>", unsafe_allow_html=True)
                    
                st.markdown("<hr/>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style="display:flex; align-items:center; margin-bottom: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M12 13V2l4 4"/><path d="m12 2-4 4"/><path d="M20 13v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6"/></svg>
                    <h5 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.05rem; font-weight:700;">Commit Diagnostic to Ledger</h5>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("commit_ledger_form"):
                    target_patient_id = st.text_input("Verify Patient Username ID", placeholder="e.g. test_patient")
                    target_ehr_id = st.text_input("Target EHR ID to Evaluate (Optional)", placeholder="e.g. ehr_1234abcd", help="Enter the ID of an existing manual upload to update it with this AI evaluation.")
                    notes = st.text_area("Physician Diagnostic Observations", placeholder="Enter specific instructions or diagnostics findings...", height=80)
                    commit_btn = st.form_submit_button("Sign & Anchors Record to Fabric ΓåÆ", type="primary", use_container_width=True)
                    
                if commit_btn:
                    if not target_patient_id:
                        st.error("Patient Username ID is required to anchor a record.")
                    else:
                        with st.spinner("Compiling PDF, uploading to IPFS, and calling smart contract..."):
                            try:
                                payload = {
                                    "patient_id": target_patient_id.strip(),
                                    "vitals": vitals,
                                    "doctor_notes": notes.strip(),
                                    "target_ehr_id": target_ehr_id.strip() if target_ehr_id else ""
                                }
                                res = requests.post(f"{API_BASE_URL}/create_prediction_record", json=payload, headers=api_headers())
                                
                                if res.status_code == 200:
                                    res_data = res.json()
                                    st.success("Γ£à EHR Diagnostic record securely committed to Blockchain ledger!")
                                    st.markdown(f"**EHR ID:** {format_hash_badge(res_data.get('record_id'))}", unsafe_allow_html=True)
                                    st.markdown(f"**IPFS CID:** {format_hash_badge(res_data.get('ipfs_hash'), 10, 6)}", unsafe_allow_html=True)
                                    st.caption("A professional PDF report was automatically generated, pinned to IPFS, and metadata was anchored on-ledger.")
                                    
                                    try:
                                        pdf_res = requests.get(f"{API_BASE_URL}/download_report/{res_data.get('record_id')}", headers=api_headers())
                                        if pdf_res.status_code == 200:
                                            st.download_button(
                                                label="≡ƒôÑ Download Newly Generated Report PDF",
                                                data=pdf_res.content,
                                                file_name=f"report_{res_data.get('record_id')}.pdf",
                                                mime="application/pdf"
                                            )
                                    except Exception:
                                        pass
                                else:
                                    st.error(f"Transaction failed: {res.text}")
                            except Exception as e:
                                st.error(f"Network error: {e}")


# ==========================================
# ADMIN PAGES
# ==========================================

elif st.session_state.role == "admin":
    
    # ΓöÇΓöÇ Admin Dashboard Summary
    if "Dashboard Summary" in page:
        st.title("Administrative Operations Dashboard")
        st.caption("Access node metrics, total ledgers statistics, and network integrity indicators.")
        
        # Load stats
        stats = {"patients": 0, "doctors": 0, "records": 0}
        with st.spinner("Querying admin metrics..."):
            try:
                res = requests.get(f"{API_BASE_URL}/admin/stats", headers=api_headers())
                if res.status_code == 200:
                    stats = res.json()
            except Exception as e:
                st.error(f"Stats retrieval failed: {e}")
                
        # Stats metrics grid
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-card-label">Registered Patients</div>
                <div class="metric-card-value">{stats['patients']}</div>
                <div class="metric-card-footer">SQLite Auth Nodes</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Certified Doctors</div>
                <div class="metric-card-value">{stats['doctors']}</div>
                <div class="metric-card-footer">Endorsing Practitioner identities</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Blockchain Records</div>
                <div class="metric-card-value">{stats['records']}</div>
                <div class="metric-card-footer">Total smart contract assets committed</div>
            </div>
            <div class="metric-card">
                <div class="metric-card-label">Node Network Health</div>
                <div class="metric-card-value" style="color:#10B981;">100% ONLINE</div>
                <div class="metric-card-footer">Hyperledger Fabric &amp; IPFS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display:flex; align-items:center; margin-bottom: 1.25rem; margin-top: 1.75rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z"/><path d="M12 22V12"/><path d="m9 15 3-3 3 3"/></svg>
            <h3 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.35rem; font-weight:700;">Global Ledger Audit Trail</h3>
        </div>
        """, unsafe_allow_html=True)
        
        records = []
        with st.spinner("Retrieving global ledger records..."):
            try:
                res = requests.get(f"{API_BASE_URL}/get_records", headers=api_headers())
                if res.status_code == 200:
                    records = sort_records_chronologically(res.json())
                else:
                    st.error(f"Failed to query global ledger: {res.text}")
            except Exception as e:
                st.error(f"Ledger connection failed: {e}")
            
        if not records:
            st.info("No records are registered on the ledger.")
        else:
            df_recs = []
            for r in reversed(records):
                pred_meta = parse_blockchain_prediction(r.get("mlPrediction"))
                df_recs.append({
                    "Asset ID": r.get("id"),
                    "Patient ID": r.get("patientId"),
                    "IPFS Hash": r.get("ipfsHash"),
                    "Diagnosis": pred_meta.get("prediction"),
                    "Risk Level": pred_meta.get("risk_level"),
                    "Authorized Nodes": len(r.get("authorizedUsers", []))
                })
            st.dataframe(pd.DataFrame(df_recs), use_container_width=True)

    # ΓöÇΓöÇ Admin User Directory Page
    elif "User Directory" in page:
        st.title("Secure User Node Registry")
        st.caption("List of all registered participant nodes on the local identity database.")
        
        users = []
        with st.spinner("Fetching directory listing..."):
            try:
                res = requests.get(f"{API_BASE_URL}/admin/users", headers=api_headers())
                if res.status_code == 200:
                    users = res.json()
            except Exception as e:
                st.error(f"Failed to fetch directory: {e}")
                
        if not users:
            st.info("No users registered.")
        else:
            df_users = pd.DataFrame(users)
            df_users.columns = ["User Database ID", "Username / Node ID", "Assigned System Role"]
            
            search_u = st.text_input("≡ƒöì Filter Username", "").strip().lower()
            if search_u:
                df_users = df_users[df_users["Username / Node ID"].str.lower().str.contains(search_u)]
                
            st.dataframe(df_users, use_container_width=True)

    # ΓöÇΓöÇ Admin Docker & Network Diagnostics Page
    elif "Network Diagnostics" in page:
        st.title("Distributed Infrastructure Diagnostics")
        st.caption("Active container state monitoring for Hyperledger Fabric test-network and IPFS IPFS daemon nodes.")
        
        col_c, col_d = st.columns([5, 3])
        
        with col_c:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom: 1.25rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="20" height="8" x="2" y="3" rx="2"/><rect width="20" height="8" x="2" y="13" rx="2"/><line x1="6" x2="6.01" y1="7" y2="7"/><line x1="6" x2="6.01" y1="17" y2="17"/></svg>
                <h3 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.2rem; font-weight:700;">Docker Infrastructure Monitor</h3>
            </div>
            """, unsafe_allow_html=True)
            
            containers = []
            try:
                res = requests.get(f"{API_BASE_URL}/admin/docker_status", headers=api_headers())
                if res.status_code == 200:
                    containers = res.json().get("containers", [])
            except Exception as e:
                st.error(f"Cannot connect to Docker daemon monitor: {e}")
                
            if not containers:
                st.warning("No docker containers discovered. Ensure Docker Desktop or Daemon is active.")
            else:
                for c in containers:
                    status = c.get("status")
                    dot_color = "≡ƒƒó" if "Up" in status else "≡ƒö┤"
                    st.markdown(f"""
                    <div class="flat-card" style="padding:0.85rem 1.15rem; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:#0F172A; font-size:0.9rem; font-family:'Plus Jakarta Sans';">{c.get('name')}</span><br/>
                            <span style="font-size:0.75rem; color:#64748B;">Image: <code>{c.get('image')}</code></span>
                        </div>
                        <span style="font-size:0.8rem; font-weight:600;">{dot_color} {status}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with col_d:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom: 1.25rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/></svg>
                <h3 style="margin:0; color:#0F172A; font-family:'Plus Jakarta Sans'; font-size:1.2rem; font-weight:700;">Network Gateways &amp; Ports</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="flat-card">
                <div style="font-weight:700; font-size:0.8rem; color:#64748B; margin-bottom:4px; font-family:'Plus Jakarta Sans'; text-transform:uppercase; letter-spacing:0.04em;">Flask REST Backend</div>
                <div style="font-family:monospace; font-size:0.88rem; color:#0F172A; margin-bottom:12px; font-weight:600;">http://127.0.0.1:5000</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:#64748B; margin-bottom:4px; font-family:'Plus Jakarta Sans'; text-transform:uppercase; letter-spacing:0.04em;">IPFS API Node Endpoint</div>
                <div style="font-family:monospace; font-size:0.88rem; color:#0F172A; margin-bottom:12px; font-weight:600;">http://127.0.0.1:5001</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:#64748B; margin-bottom:4px; font-family:'Plus Jakarta Sans'; text-transform:uppercase; letter-spacing:0.04em;">Local IPFS HTTP Gateway</div>
                <div style="font-family:monospace; font-size:0.88rem; color:#0F172A; margin-bottom:12px; font-weight:600;">http://127.0.0.1:8080</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:#64748B; margin-bottom:4px; font-family:'Plus Jakarta Sans'; text-transform:uppercase; letter-spacing:0.04em;">Fabric Orderer Node</div>
                <div style="font-family:monospace; font-size:0.88rem; color:#0F172A; margin-bottom:12px; font-weight:600;">orderer.example.com:7050</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:#64748B; margin-bottom:4px; font-family:'Plus Jakarta Sans'; text-transform:uppercase; letter-spacing:0.04em;">Fabric Peer Org1 Node</div>
                <div style="font-family:monospace; font-size:0.88rem; color:#0F172A; margin-bottom:12px; font-weight:600;">peer0.org1.example.com:7051</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:#64748B; margin-bottom:4px; font-family:'Plus Jakarta Sans'; text-transform:uppercase; letter-spacing:0.04em;">Fabric Peer Org2 Node</div>
                <div style="font-family:monospace; font-size:0.88rem; color:#0F172A; font-weight:600;">peer0.org2.example.com:9051</div>
            </div>
            """, unsafe_allow_html=True)
