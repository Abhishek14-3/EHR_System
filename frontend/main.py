import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
API_BASE_URL = "http://127.0.0.1:5000"

# ==========================================
# DARK MODE DOM OBSERVER & LOGIC
# ==========================================
components.html("""
<script>
    const parent = window.parent.document;
    
    // 1. Initial Load - set the theme attribute instantly
    if (!parent.documentElement.hasAttribute('data-theme')) {
        const saved = window.localStorage.getItem('healthchain_theme');
        const pref = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        parent.documentElement.setAttribute('data-theme', saved || pref);
    }
    
    // 2. Continuous Observer to attach toggle button
    const observer = new MutationObserver(() => {
        const container = parent.getElementById("theme-btn-target");
        if (container && !parent.getElementById("hc-theme-toggle")) {
            const btn = parent.createElement("button");
            btn.id = "hc-theme-toggle";
            btn.className = "hc-theme-toggle-btn"; 
            btn.setAttribute("aria-label", "Toggle dark mode");
            
            const updateBtn = () => {
                const current = parent.documentElement.getAttribute('data-theme');
                btn.innerHTML = current === 'dark' ? '☀️ Light' : '🌙 Dark';
            };
            
            updateBtn();
            
            btn.onclick = () => {
                const isDark = parent.documentElement.getAttribute('data-theme') === 'dark';
                const next = isDark ? 'light' : 'dark';
                parent.documentElement.setAttribute('data-theme', next);
                window.localStorage.setItem('healthchain_theme', next);
                updateBtn();
            };
            
            container.appendChild(btn);
        }
    });
    
    observer.observe(parent.body, { childList: true, subtree: true });
</script>
""", height=0, width=0)

# Force sidebar to be expanded by default so navigation is never hidden
st.set_page_config(
    page_title="HealthChain AI | Clinical EHR Platform",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PREMIER BIO-CLINICAL SLATE DESIGN SYSTEM
# Typography: Plus Jakarta Sans (Interface) & JetBrains Mono (Cryptographic Data)
# Dark Mode: Obsidian Crypt (#090D16, #0F172A, #06B6D4, #6366F1)
# Light Mode: Clinical Alabaster (#F8FAFC, #FFFFFF, #0284C7, #4F46E5)
# Triage System: Emerald #10B981, Amber #F59E0B, Rose #F43F5E, Violet #8B5CF6
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300..800;1,300..800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* =========================================================================
       CLINICAL ALABASTER LIGHT DESIGN TOKENS (LIGHT MODE)
       ========================================================================= */
    :root {
        --bg:          #F8FAFC;
        --surface:     #FFFFFF;
        --surface-2:   #F1F5F9;
        --sidebar-bg:  #FFFFFF;
        --accent:      #0284C7;
        --accent-h:    #0369A1;
        --accent-lt:   #E0F2FE;
        --accent-ring: rgba(2, 132, 199, 0.25);
        --tech:        #4F46E5;
        --tech-lt:     rgba(79, 70, 229, 0.1);
        --border:      #E2E8F0;
        --border-2:    #CBD5E1;
        --t1:          #0F172A;
        --t2:          #64748B;
        --t3:          #94A3B8;
        --low:         #10B981;
        --moderate:    #F59E0B;
        --high:        #F43F5E;
        --audit:       #8B5CF6;
        --neutral:     #94A3B8;
        --r-lg: 16px;
        --r-md: 12px;
        --r-sm: 10px;
        --s-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
        --s-sm: 0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04);
        --s-md: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -1px rgba(15, 23, 42, 0.04);
        --s-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -2px rgba(15, 23, 42, 0.04);
        --btn-text:    #FFFFFF;
    }
    
    /* =========================================================================
       OBSIDIAN CRYPT DARK DESIGN TOKENS (DARK MODE)
       ========================================================================= */
    [data-theme="dark"] {
        --bg:          #090D16;
        --surface:     #0F172A;
        --surface-2:   #1E293B;
        --sidebar-bg:  #0F172A;
        --accent:      #06B6D4;
        --accent-h:    #22D3EE;
        --accent-lt:   rgba(6, 182, 212, 0.15);
        --accent-ring: rgba(6, 182, 212, 0.35);
        --tech:        #6366F1;
        --tech-lt:     rgba(99, 102, 241, 0.15);
        --border:      rgba(148, 163, 184, 0.12);
        --border-2:    rgba(148, 163, 184, 0.24);
        --t1:          #F8FAFC;
        --t2:          #94A3B8;
        --t3:          #64748B;
        --low:         #10B981;
        --moderate:    #F59E0B;
        --high:        #F43F5E;
        --audit:       #8B5CF6;
        --neutral:     #94A3B8;
        --btn-text:    #090D16;
    }

    html, body, * { font-family: 'Plus Jakarta Sans',system-ui,sans-serif !important; -webkit-font-smoothing: antialiased; box-sizing: border-box; }
    
    .stApp, section[data-testid="stSidebar"], .flat-card, .metric-card, .auth-card, [data-baseweb="select"] > div:first-child, [data-testid="stFileUploader"] {
        transition: background-color 0.35s ease, border-color 0.35s ease !important;
    }
    .hc-theme-toggle-btn {
        background: var(--surface) !important; color: var(--t1) !important; border: 1.5px solid var(--border) !important;
        border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.88rem !important;
        padding: 0.52rem 1.1rem !important; box-shadow: var(--s-xs) !important; width: 100% !important;
        transition: border-color 0.15s, box-shadow 0.15s, transform 0.1s, background-color 0.4s ease, color 0.4s ease !important;
        cursor: pointer !important; font-family: 'Plus Jakarta Sans',sans-serif !important;
    }
    .hc-theme-toggle-btn:hover {
        border-color: var(--border-2) !important; box-shadow: var(--s-sm) !important; transform: translateY(-1px) !important;
    }
    
    .stApp { background: var(--bg) !important; }
    .block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px !important; }

    h1,h2,h3,h4,h5,h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Plus Jakarta Sans',sans-serif !important;
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
    #MainMenu,footer,header,[data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
    .stDeployButton,[data-testid="stStatusWidget"] { display: none !important; }
    iframe[height="0"] { display: none !important; }
    .element-container:has(iframe[height="0"] ) { display: none !important; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] { background: var(--sidebar-bg) !important; border-right: 1px solid var(--border) !important; }
    section[data-testid="stSidebar"] * { color: var(--t1) !important; font-family: 'Plus Jakarta Sans',sans-serif !important; }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--t3) !important; font-size: 0.7rem !important; font-weight: 700 !important; letter-spacing: 0.09em !important; text-transform: uppercase !important; }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span { color: var(--t2) !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] { display: flex !important; flex-direction: column !important; gap: 2px !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label { color: var(--t2) !important; font-size: 0.88rem !important; font-weight: 500 !important; padding: 9px 14px !important; border-radius: var(--r-sm) !important; transition: background 0.12s,color 0.12s !important; cursor: pointer !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: var(--accent-lt) !important; color: var(--accent) !important; }
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] .stButton button { background: var(--high) !important; border: none !important; color: #FFFFFF !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.87rem !important; padding: 0.55rem 1rem !important; width: 100% !important; margin-top: 1.5rem !important; box-shadow: none !important; transition: opacity 0.15s, transform 0.1s !important; }
    section[data-testid="stSidebar"] button:hover { opacity: 0.9 !important; transform: none !important; }

    /* INPUTS & PASSWORD TOGGLE */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea { background: var(--surface) !important; border: 1.5px solid var(--border) !important; border-radius: var(--r-sm) !important; color: var(--t1) !important; font-size: 0.9rem !important; padding: 0.55rem 0.85rem !important; box-shadow: var(--s-xs) !important; transition: border-color 0.15s,box-shadow 0.15s !important; }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-ring) !important; outline: none !important; }
    
    [data-testid="stTextInput"] button,
    [data-baseweb="input"] button {
        background: transparent !important;
        border: none !important;
        color: var(--t2) !important;
        box-shadow: none !important;
        width: auto !important;
        margin: 0 !important;
        padding: 4px 8px !important;
    }
    [data-testid="stTextInput"] button:hover,
    [data-baseweb="input"] button:hover {
        background: transparent !important;
        color: var(--accent) !important;
        transform: none !important;
    }
    [data-testid="stTextInput"] button svg,
    [data-baseweb="input"] button svg {
        fill: var(--t2) !important;
    }

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
    [data-testid="stFileUploader"] button { background: var(--accent-lt) !important; color: var(--accent) !important; border: 1px solid var(--border-2) !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.82rem !important; padding: 0.35rem 0.9rem !important; margin-top: 0 !important; width: auto !important; box-shadow: none !important; }
    [data-testid="stFileUploader"] button:hover { opacity: 0.85 !important; transform: none !important; box-shadow: none !important; }

    /* SLIDER */
    [data-testid="stSlider"] > div > div > div { background: var(--border) !important; }
    [data-testid="stSlider"] [role="slider"] { background: var(--accent) !important; border: 2px solid var(--surface) !important; box-shadow: var(--s-sm),0 0 0 2px var(--accent) !important; width: 18px !important; height: 18px !important; }
    [data-testid="stSlider"] > div > div > div > div { background: var(--accent) !important; }
    [data-testid="stSlider"] [data-testid="stTickBarMin"],[data-testid="stSlider"] [data-testid="stTickBarMax"] { color: var(--t3) !important; font-size: 0.78rem !important; }

    /* FORM & AUTH CONTAINERS */
    div[data-testid="stForm"] {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        padding: 2rem 2.25rem !important;
        box-shadow: var(--s-sm) !important;
    }

    /* BUTTONS */
    [data-testid="stFormSubmitButton"] button,
    button[kind="primary"],
    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        color: var(--btn-text) !important;
        border: none !important;
        border-radius: var(--r-sm) !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 1px 3px rgba(6,182,212,.25) !important;
        transition: background 0.15s,box-shadow 0.15s,transform 0.1s !important;
        cursor: pointer !important;
    }
    [data-testid="stFormSubmitButton"] button:hover,
    button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-h) !important;
        box-shadow: 0 4px 14px rgba(6,182,212,.35) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stFormSubmitButton"] button:active,button[kind="primary"]:active { transform: translateY(0) !important; }
    button[kind="secondary"],.stButton > button[kind="secondary"] { background: var(--surface-2) !important; color: var(--t1) !important; border: 1.5px solid var(--border) !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.88rem !important; padding: 0.52rem 1.1rem !important; box-shadow: var(--s-xs) !important; transition: border-color 0.15s,box-shadow 0.15s,transform 0.1s !important; }
    button[kind="secondary"]:hover,.stButton > button[kind="secondary"]:hover { border-color: var(--border-2) !important; box-shadow: var(--s-sm) !important; transform: translateY(-1px) !important; }
    [data-testid="stDownloadButton"] button { background: var(--accent-lt) !important; color: var(--accent) !important; border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important; font-weight: 600 !important; font-size: 0.84rem !important; padding: 0.42rem 1rem !important; box-shadow: none !important; margin-top: 0 !important; transition: background 0.15s !important; }
    [data-testid="stDownloadButton"] button:hover { opacity: 0.85 !important; transform: none !important; box-shadow: none !important; }

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

    /* TRIAGE BADGES */
    .badge { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; }
    .badge-low      { background: rgba(16, 185, 129, 0.12); color: var(--low); border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-moderate { background: rgba(245, 158, 11, 0.12); color: var(--moderate); border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-high     { background: rgba(244, 63, 94, 0.12); color: var(--high); border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-audit    { background: rgba(139, 92, 246, 0.12); color: var(--audit); border: 1px solid rgba(139, 92, 246, 0.3); }
    .badge-na,.badge-info { background: var(--surface-2); color: var(--t3); border: 1px solid var(--border); }

    /* HASH & CRYPTOGRAPHIC BADGES */
    .hash-badge { display: inline-block; background: var(--surface-2); color: var(--tech); border: 1px solid var(--border); border-radius: 6px; padding: 2px 8px; font-family: 'JetBrains Mono',Consolas,monospace !important; font-size: 0.78rem; font-weight: 600; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; vertical-align: middle; cursor: default; transition: background 0.12s; }
    .hash-badge:hover { background: var(--border); }
    code { background: var(--surface-2) !important; color: var(--tech) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; padding: 2px 7px !important; font-family: 'JetBrains Mono',Consolas,monospace !important; font-size: 0.82em !important; }

    /* TIMELINE */
    .timeline-track { position: relative; margin-left: 10px; padding-left: 28px; border-left: 2px solid var(--border); padding-bottom: 1.25rem; }
    .timeline-dot   { position: absolute; left: -7px; top: 20px; width: 12px; height: 12px; border-radius: 50%; background: var(--surface); z-index: 2; }
    .timeline-dot-low      { border: 3px solid var(--low) !important;      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important; }
    .timeline-dot-moderate { border: 3px solid var(--moderate) !important;  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2) !important; }
    .timeline-dot-high     { border: 3px solid var(--high) !important;      box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.2) !important; }
    .timeline-dot-na       { border: 3px solid var(--neutral) !important;   box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.2) !important; }
    .timeline-card-low      { border-left: 3px solid var(--low) !important; }
    .timeline-card-moderate { border-left: 3px solid var(--moderate) !important; }
    .timeline-card-high     { border-left: 3px solid var(--high) !important; }
    .timeline-card-na       { border-left: 3px solid var(--neutral) !important; }

    /* AUTH */
    .brand-panel { background: transparent; padding: 1.5rem 1rem; min-height: 520px; display: flex; flex-direction: column; }
    .brand-eyebrow { font-size: 0.78rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 1rem 0; }
    .brand-title { font-size: 2.2rem !important; font-weight: 700 !important; color: var(--t1) !important; letter-spacing: -0.02em !important; margin: 0 0 1.25rem 0 !important; line-height:1.25 !important; }
    .brand-desc  { font-size: 0.95rem !important; color: var(--t2) !important; line-height: 1.6 !important; margin-bottom: 2.5rem !important; }
    .brand-feat  { display: flex; align-items: center; gap: 1rem; font-size: 0.9rem; color: var(--t1); font-weight: 500; margin-bottom: 1.25rem; }
    .feat-icon   { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: var(--accent-lt); color: var(--accent); border-radius: 8px; border: 1px solid var(--border); flex-shrink: 0; }
    .brand-chips { display: flex; gap: 10px; margin-top: auto; padding-top: 2rem; flex-wrap: wrap; }
    .tech-chip   { font-size: 0.75rem; font-weight: 600; color: var(--t2); padding: 5px 14px; border: 1px solid var(--border); border-radius: 99px; background: var(--surface-2); letter-spacing: 0.02em; }
    .auth-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); padding: 2rem 2rem 2.25rem; box-shadow: var(--s-sm); max-width: 440px; margin: 0 auto; }
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
# GLOBAL HEADER
# ==========================================
st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
col_hdr_left, col_hdr_right = st.columns([9, 1], vertical_alignment="center")
with col_hdr_left:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h5v5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/></svg>
        <h3 style="color: var(--t1); margin: 0; font-size: 1.15rem; font-family:'DM Sans'; font-weight:700; letter-spacing:-0.03em;">HealthChain AI</h3>
    </div>
    """, unsafe_allow_html=True)
with col_hdr_right:
    st.markdown("<div id='theme-btn-target'></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ==========================================
# AUTH PORTAL (LOGIN / REGISTER)
# ==========================================

if 'token' not in st.session_state:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "login"

    col_brand, col_form = st.columns([1.1, 1], gap="large", vertical_alignment="center")
    
    with col_brand:
        st.markdown(
"""<div class="brand-panel">
<p class="brand-eyebrow">Decentralized Health Records</p>
<h1 class="brand-title">Your records, secured and<br>under your control</h1>
<p class="brand-desc">
Clinical EHR powered by Scikit-Learn ML, Hyperledger Fabric smart contracts, and IPFS storage.
</p>

<div class="brand-feat">
<div class="feat-icon">
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
</div>
Patient-controlled permissions via smart contracts
</div>

<div class="brand-feat">
<div class="feat-icon">
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
</div>
Gradient boosting predictive analysis
</div>

<div class="brand-feat">
<div class="feat-icon">
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" x2="12" y1="22.08" y2="12"/></svg>
</div>
Immutable file hosting on IPFS nodes
</div>

<div class="brand-chips">
<span class="tech-chip">Hyperledger Fabric</span>
<span class="tech-chip">IPFS</span>
<span class="tech-chip">Scikit-Learn</span>
</div>
</div>""", unsafe_allow_html=True)
        
    with col_form:
        with st.container(border=True):
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
                <div style="text-align: left; margin-bottom: 1.5rem;">
                    <h2 style="margin: 0; color: var(--t1); font-size: 1.65rem; font-family:'Plus Jakarta Sans',sans-serif; font-weight: 700; letter-spacing:-0.03em;">Portal access</h2>
                    <p style="color: var(--t3); font-size: 0.92rem; margin-top:5px;">Authenticate your node keys on the network.</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("login_form"):
                    username = st.text_input("Username identifier", placeholder="doctor_smith")
                    password = st.text_input("Security key", type="password", placeholder="••••••••••")
                    
                    st.markdown("""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin:-8px 0 15px 0;">
                        <span style="font-size:0.82rem; color:var(--t3);">Node: mainnet-01</span>
                        <a href="#" style="font-size:0.82rem; color:var(--accent); text-decoration:none; font-weight:500;">Forgot your key?</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    login_submit = st.form_submit_button("Authenticate identity 🔐", type="primary", use_container_width=True)
                    
                    st.markdown("""
                    <div style="text-align:center; font-size:0.82rem; color:var(--t3); margin-top:1.15rem;">
                        🔒 End-to-end encrypted session
                    </div>
                    """, unsafe_allow_html=True)
                    
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
                <div style="text-align: left; margin-bottom: 1.5rem;">
                    <h2 style="margin: 0; color: var(--t1); font-size: 1.65rem; font-family:'Plus Jakarta Sans',sans-serif; font-weight: 700; letter-spacing:-0.03em;">Node Registration</h2>
                    <p style="color: var(--t3); font-size: 0.92rem; margin-top:5px;">Register a new participant on the network</p>
                </div>
                """, unsafe_allow_html=True)

                with st.form("register_form"):
                    new_username = st.text_input("Choose Username Identifier", placeholder="e.g. patient_doe")
                    new_password = st.text_input("Choose Secure Password", type="password")
                    role = st.selectbox("Assign System Role", ["patient", "doctor", "admin"])
                    register_submit = st.form_submit_button("Create Identity Ledger Key →", type="primary", use_container_width=True)
                    
                if register_submit:
                    if not new_username or not new_password:
                        st.error("Fields cannot be empty.")
                    else:
                        with st.spinner("Registering node identity..."):
                            try:
                                res = requests.post(f"{API_BASE_URL}/register",
                                                    json={"username": new_username, "password": new_password, "role": role})
                                if res.status_code == 201:
                                    st.session_state.reg_success = f"✅ Node identity '{new_username}' registered successfully! Please log in."
                                    st.session_state.auth_mode = "login"
                                    st.rerun()
                                else:
                                    st.error(res.json().get('message', 'Registration rejected.'))
                            except Exception as e:
                                st.error(f"Failed to connect to Flask API server. {e}")

    st.stop()


# ==========================================
# MAIN NAVIGATION (Replaced Sidebar)
# ==========================================

col_nav1, col_nav2 = st.columns([8.5, 1.5], vertical_alignment="bottom")

with col_nav1:
    _role = st.session_state.get('role', '')
    _username = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
        <div style="display:inline-block; background: var(--accent-lt); border: 1px solid var(--accent); color: var(--accent); border-radius: 999px; padding: 4px 14px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; font-family:'DM Sans';">
            {_role} &bull; 👤 {_username.capitalize()}
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
        nav_state = st.session_state.get("doctor_nav", "Shared Records")

        def _update_nav():
            st.session_state.doctor_nav = st.session_state[f"radio_{nav_state}"]

        page = st.radio(
            "Navigation",
            ["Shared Records", "AI Clinical Assistant"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if nav_state == "Shared Records" else 1,
            key=f"radio_{nav_state}",
            on_change=_update_nav
        )
    elif st.session_state.role == "admin":
        page = st.radio(
            "Navigation",
            ["Dashboard Summary", "User Directory", "Network Diagnostics"],
            horizontal=True,
            label_visibility="collapsed"
        )

with col_nav2:
    if st.button("🚪 Log Out", use_container_width=True):
        trigger_logout()

st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 2rem; border-color: var(--border);'>", unsafe_allow_html=True)


# ==========================================
# PATIENT PAGES
# ==========================================

if st.session_state.role == "patient":
    
    # ── Patient Dashboard Overview
    if "Dashboard Overview" in page:
        st.title("Patient EHR Dashboard")
        st.caption("Access your health history, medical scans, and automated AI health reports.")
        
        # Load Patient Records
        records = st.session_state.get("patient_records_cache", [])
        if not records:
            with st.spinner("Syncing data with Hyperledger Fabric..."):
                try:
                    res = requests.get(f"{API_BASE_URL}/get_my_records", headers=api_headers())
                    if res.status_code == 200:
                        records = sort_records_chronologically(res.json())
                        st.session_state.patient_records_cache = records
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
                <div class="metric-card-value" style="color:var(--high);">ACTIVE</div>
                <div class="metric-card-footer">Double Endorsed Node Network</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Lucide ClipboardList SVG Header
        st.markdown("""
        <div style="display:flex; align-items:center; margin-bottom: 1.25rem; margin-top: 1.75rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/></svg>
            <h3 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.35rem; font-weight:700;">Your Health Record Timeline</h3>
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
                                <h4 style="margin:0 0 4px 0; color:var(--t1); font-family:var(--font-h2); font-weight:700; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
                                    EHR ID: {format_hash_badge(rec_id)}
                                </h4>
                                <p style="margin:2px 0; font-size:0.82rem; color:var(--t2); font-family:var(--font-body);">Uploaded: {pred_meta.get('timestamp', 'N/A')}</p>
                            </div>
                            <span class="badge {badge_class}">{ "⏳ Pending Review" if pred_meta.get('type') == 'manual' else f"{pred_meta.get('prediction')} · {pred_meta.get('risk_level')}" }</span>
                        </div>
                        <div style="margin-top: 10px; font-size: 0.88rem; color:var(--t1); line-height: 1.8; font-family:var(--font-body);">
                            <strong>Doctor Observations:</strong> {pred_meta.get('doctor_notes', 'N/A')}
                        </div>
                        <div style="margin-top: 8px; font-size: 0.78rem; color:var(--t2); display:flex; align-items:center; gap:6px; font-family:var(--font-body);">
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
                                    label="📥 Clinical PDF Report",
                                    data=pdf_res.content,
                                    file_name=f"clinical_report_{rec_id}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_patient_{rec_id}"
                                )
                        except Exception:
                            st.caption("PDF unavailable")
                    else:
                        ipfs_gateway = f"http://127.0.0.1:8080/ipfs/{ipfs_hash}"
                        st.markdown(f"[🔗 View Document]({ipfs_gateway})")
                st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)
                
    # ── Patient Upload File
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
                submit_file = st.form_submit_button("Store & Inscribe Record →", type="primary", use_container_width=True)
                
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
                                st.success("✅ File securely stored on IPFS & Blockchain!")
                                st.markdown(f"**EHR Record ID:** {format_hash_badge(res_data.get('record_id'))}", unsafe_allow_html=True)
                                st.markdown(f"**IPFS CID:** {format_hash_badge(res_data.get('ipfs_hash'), 10, 6)}", unsafe_allow_html=True)
                                st.info("This file is private. Only you can access it until you explicitly authorize a clinician.")
                                if "patient_records_cache" in st.session_state:
                                    del st.session_state["patient_records_cache"]
                            else:
                                st.error(f"Transaction failed: {res.text}")
                        except Exception as e:
                            st.error(f"Network error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_y:
            st.markdown("""
            <div class="flat-card" style="background:var(--surface); border-left:4px solid var(--high);">
                <div style="display:flex; align-items:center; margin-bottom: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                    <h4 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-weight:700;">Decoupled Storage Flow</h4>
                </div>
                <p style="font-size:0.9rem; color:var(--t1); line-height:1.8; margin:0; font-family:var(--font-body);">
                    Raw medical documents are saved onto <strong>IPFS (InterPlanetary File System)</strong>. 
                    IPFS hashes (CIDs) are immutable. This CID, combined with your Patient ID, is written onto the 
                    <strong>Hyperledger Fabric Smart Contract</strong>. 
                    No raw files are stored on-ledger, ensuring perfect privacy and high performance.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ── Patient Access Control Page
    elif "Access Delegation" in page:
        st.title("Access Delegation Control")
        st.caption("You control your privacy. Delegate viewing authorization to clinics and doctors on the network.")
        
        # Load Patient's Records for selection
        records = st.session_state.get("patient_records_cache", [])
        if not records:
            try:
                res = requests.get(f"{API_BASE_URL}/get_my_records", headers=api_headers())
                if res.status_code == 200:
                    records = res.json()
                    st.session_state.patient_records_cache = records
            except Exception as e:
                st.error(f"Failed to fetch records: {e}")
            
        col_x, col_y = st.columns([5, 4], gap="large")
        with col_x:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom:1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z"/><path d="m9 12 2 2 4-4"/></svg>
                <h4 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.15rem; font-weight:700;">Delegate Access</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if not records:
                st.info("No records found on the ledger. Upload a record before granting access.")
            else:
                record_options = {}
                for r in records:
                    pm = parse_blockchain_prediction(r.get('mlPrediction'))
                    lbl_type = "AI Diag" if pm.get('type') == 'prediction' else "Raw PDF"
                    date_val = pm.get('timestamp', 'No Date').split(' ')[0]
                    lbl = f"[{date_val}] EHR: {r.get('id')[:6]}... — {pm.get('prediction')} ({lbl_type})"
                    record_options[lbl] = r.get('id')
                
                st.markdown('<div class="flat-card">', unsafe_allow_html=True)
                with st.form("grant_access_form"):
                    selected_label = st.selectbox("Choose Medical Record", list(record_options.keys()))
                    doctor_username = st.text_input("Enter Doctor's Username", placeholder="e.g. dr_smith")
                    patient_id_auth = st.text_input("Secure Identification Number", type="password", placeholder="Enter your ID or PIN to authorize")
                    submit_grant = st.form_submit_button("Grant Ledger Access Keys →", type="primary", use_container_width=True)
                    
                if submit_grant:
                    record_id = record_options[selected_label]
                    if not doctor_username:
                        st.error("Please enter a doctor's username.")
                    elif not patient_id_auth:
                        st.error("Identification Number is required to authorize the transaction.")
                    else:
                        with st.spinner("Authenticating ID & Updating smart contract ledger access lists..."):
                            try:
                                res = requests.post(f"{API_BASE_URL}/grant_access",
                                                    json={"record_id": record_id, "doctor_id": doctor_username},
                                                    headers=api_headers())
                                if res.status_code == 200:
                                    st.success(f"✅ Identity Verified! Immutable access granted to Dr. {doctor_username}.")
                                    if "patient_records_cache" in st.session_state:
                                        del st.session_state["patient_records_cache"]
                                    st.rerun()
                                else:
                                    st.error(f"Failed to grant access: {res.text}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
                
        with col_y:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom:1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                <h4 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.15rem; font-weight:700;">Ledger Access Lists</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if not records:
                st.caption("No authorizations to display.")
            else:
                for rec in records:
                    st.markdown(f"""
                    <div class="flat-card" style="padding:1rem 1.25rem; margin-bottom:10px;">
                        <div style="font-weight:700; color:var(--t1); font-size:0.9rem; font-family:var(--font-h2); display:flex; align-items:center; gap:6px;">
                            <span>Record ID:</span> {format_hash_badge(rec.get('id'))}
                        </div>
                        <div style="font-size:0.85rem; color:var(--t2); margin-top:6px; font-family:var(--font-body);">
                            <strong>Authorized Nodes:</strong> {", ".join(rec.get('authorizedUsers', []))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# ==========================================
# DOCTOR PAGES
# ==========================================

elif st.session_state.role == "doctor":
    
    # ── Doctor Dashboard: Shared Records
    if "Shared Records" in page:
        st.title("Patient Medical Directory")
        st.caption("Access all clinical data and health predictions explicitly shared with your clinical identity.")
        
        # Load Records Shared with Doctor
        records = st.session_state.get("doctor_records_cache", [])
        if not records:
            with st.spinner("Querying secure Hyperledger Fabric ledger..."):
                try:
                    res = requests.get(f"{API_BASE_URL}/get_records_by_doctor", headers=api_headers())
                    if res.status_code == 200:
                        records = sort_records_chronologically(res.json())
                        st.session_state.doctor_records_cache = records
                except Exception as e:
                    st.error(f"Ledger connection failed: {e}")
                
        if not records:
            st.info("📭 No patient records have been shared with your clinician account yet.")
        else:
            # Search, Filter, Sort Controls
            st.markdown('<div class="flat-card" style="padding:1rem 1.25rem;">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([4, 3, 3, 2])
            
            with col1:
                search_query = st.text_input("🔍 Search Patients", placeholder="Enter Patient ID...").strip()
            with col2:
                record_types = ["All Types", "AI Prediction Reports", "Manual Uploads"]
                type_filter = st.selectbox("📁 Document Type", record_types)
            with col3:
                conditions = ["All Conditions", "Healthy", "Arthritis", "Asthma", "Cancer", "Diabetes", "Hypertension", "Obesity"]
                cond_filter = st.selectbox("🧬 Diagnostic Filter", conditions)
            with col4:
                sort_order = st.selectbox("⏳ Sort Date", ["Newest First", "Oldest First"])
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
                    card_border = "var(--high)"
                elif "mod" in rl:
                    badge_class = "badge-moderate"
                    card_border = "var(--high)"
                elif "low" in rl:
                    badge_class = "badge-low"
                    card_border = "var(--glass-border)"
                else:
                    badge_class = "badge-na"
                    card_border = "var(--t1)"
                    
                st.markdown(f"""
                <div class="flat-card" style="border-left: 4px solid {card_border};">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; border-bottom: 1px solid var(--surface); padding-bottom:8px; margin-bottom:10px;">
                        <div>
                            <h4 style="margin:0 0 4px 0; font-size:1.15rem; color:var(--t1); font-family:var(--font-h2); font-weight:700; display:flex; align-items:center; gap:8px;">
                                EHR Record: {format_hash_badge(rec_id)}
                            </h4>
                            <span style="font-size:0.85rem; color:var(--t2); font-family:var(--font-body);">Patient: <b>{patient_id.upper()}</b> | Date: {pred_meta.get('timestamp', 'N/A')}</span>
                        </div>
                        <span class="badge {badge_class}">{pred_meta.get('prediction')} · {pred_meta.get('risk_level')}</span>
                    </div>
                    <div style="font-size: 0.9rem; color:var(--t1); margin-bottom:10px; line-height: 1.8; font-family:var(--font-body);">
                        <strong>Physician Notes:</strong> {pred_meta.get('doctor_notes', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                
                if pred_meta.get('type') == 'manual':
                    st.markdown(f"<div style='margin-bottom: 8px;'><span style='background-color:var(--surface); color:var(--high); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; font-family:var(--font-h2);'>Pending Evaluation</span> <span style='font-size: 0.85rem; color: var(--t2); font-family:var(--font-body);'>Copy the EHR ID above and use the AI Clinical Assistant to evaluate this record.</span></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="font-size: 0.85rem; color:var(--t2); margin-bottom:12px; display:flex; align-items:center; gap:6px; font-family:var(--font-body);">
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
                                    label="📥 Download Clinical PDF",
                                    data=pdf_res.content,
                                    file_name=f"clinical_report_{rec_id}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_dr_{rec_id}"
                                )
                        except Exception:
                            st.caption("PDF unavailable")
                    else:
                        with st.expander("👁️ View Uploaded Document"):
                            st.markdown(f'<iframe src="http://127.0.0.1:8080/ipfs/{ipfs_hash}" width="100%" height="600px" style="border:1px solid var(--border); border-radius:8px;"></iframe>', unsafe_allow_html=True)
                        if st.button("🤖 Run ML Analysis on this Record", type="primary", key=f"run_ml_{rec_id}"):
                            with st.spinner("Extracting vitals and running analysis..."):
                                try:
                                    ext_res = requests.post(f"{API_BASE_URL}/extract_vitals", json={"ipfs_hash": ipfs_hash}, headers=api_headers())
                                    if ext_res.status_code == 200:
                                        raw_extracted = ext_res.json().get("vitals", {})
                                        vitals = raw_extracted.copy()
                                        
                                        default_vitals = {
                                            "Age": 55, "Gender": "Male", "Glucose": 120.0, "Blood Pressure": 140.0, 
                                            "BMI": 28.5, "Oxygen Saturation": 95.0, "LengthOfStay": 4, 
                                            "Cholesterol": 213.0, "Triglycerides": 177.0, "HbA1c": 6.3, 
                                            "Smoking": 0, "Alcohol": 0, "Physical Activity": 4, 
                                            "Diet Score": 4, "Family History": 0, "Stress Level": 6, "Sleep Hours": 6
                                        }
                                        for k, v in default_vitals.items():
                                            if k not in vitals:
                                                vitals[k] = v
                                                
                                        pred_res = requests.post(f"{API_BASE_URL}/predict", json={"vitals": vitals}, headers=api_headers())
                                        if pred_res.status_code == 200:
                                            st.session_state.last_prediction = pred_res.json()
                                            st.session_state.patient_vitals = vitals
                                            st.session_state.extracted_vitals = raw_extracted
                                            st.session_state.target_patient_id_for_commit = patient_id
                                            st.session_state.target_ehr_id_for_commit = rec_id
                                            st.session_state.target_ipfs_hash_for_analysis = ipfs_hash
                                            st.session_state.doctor_nav = "AI Clinical Assistant"
                                            st.session_state.assistant_tab = "📊 Diagnostic Results & SHAP Report"
                                            st.rerun()
                                        else:
                                            st.error(f"Failed prediction: {pred_res.text}")
                                    else:
                                        st.error(f"Failed to extract vitals: {ext_res.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                with col2:
                    ipfs_gateway = f"http://127.0.0.1:8080/ipfs/{ipfs_hash}"
                    st.markdown(f"[🔗 View Document on IPFS]({ipfs_gateway})")
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Doctor Dashboard: AI Clinical Assistant (Prediction Form)
    elif "AI Clinical Assistant" in page:
        st.title("Clinical AI Diagnostic Assistant")
        st.caption("Enter patient physiological metrics and lifestyles to perform classification diagnostics.")
        
        if 'last_prediction' not in st.session_state:
            st.session_state.last_prediction = None
            st.session_state.patient_vitals = None
            
        if 'extracted_vitals' not in st.session_state:
            st.session_state.extracted_vitals = {}
            
        if 'assistant_tab' not in st.session_state:
            st.session_state.assistant_tab = "🩺 Patient Vitals Input & Extraction"
            
        st.markdown("<style>div[role='radiogroup'] {margin-bottom: 1.5rem;}</style>", unsafe_allow_html=True)
        assist_tab = st.radio("Assistant View", ["🩺 Patient Vitals Input & Extraction", "📊 Diagnostic Results & SHAP Report"], horizontal=True, label_visibility="collapsed", key="assistant_tab")
        
        if assist_tab == "🩺 Patient Vitals Input & Extraction":
            st.subheader("Auto-Extract Vitals from Medical Report")
            with st.form("extract_form"):
                extract_ehr_id = st.text_input("Enter EHR ID to Extract Vitals", placeholder="EHR-...")
                extract_btn = st.form_submit_button("Extract Vitals from PDF")
                
            if extract_btn and extract_ehr_id:
                with st.spinner("Analyzing PDF using NLP..."):
                    records = st.session_state.get("doctor_records", [])
                    if not records:
                        try:
                            rec_res = requests.get(f"{API_BASE_URL}/get_records_by_doctor", headers=api_headers())
                            if rec_res.status_code == 200:
                                records = rec_res.json().get("records", [])
                                st.session_state.doctor_records = records
                        except:
                            pass
                            
                    target_ipfs = None
                    extract_patient_id = None
                    for r in records:
                        if r.get("recordId") == extract_ehr_id.strip():
                            target_ipfs = r.get("ipfsHash")
                            extract_patient_id = r.get("patientId")
                            break
                            
                    if not target_ipfs:
                        st.error("EHR ID not found or unauthorized. Ensure the patient has granted you access.")
                    else:
                        st.session_state.target_ipfs_hash_for_analysis = target_ipfs
                        st.session_state.target_ehr_id_for_commit = extract_ehr_id.strip()
                        st.session_state.target_patient_id_for_commit = extract_patient_id
                        try:
                            res = requests.post(f"{API_BASE_URL}/extract_vitals", json={"ipfs_hash": target_ipfs}, headers=api_headers())
                            if res.status_code == 200:
                                st.session_state.extracted_vitals = res.json().get("vitals", {})
                                st.success("✅ Vitals extracted successfully! Please review the pre-filled form below.")
                            else:
                                st.error(f"Failed to extract vitals: {res.text}")
                        except Exception as e:
                            st.error(f"Error communicating with backend: {e}")
                        
            st.subheader("Patient Vitals Input Form")
            with st.form("prediction_input_form"):
                ev = st.session_state.extracted_vitals
                has_extracted = bool(ev)
                
                if has_extracted:
                    extracted_fields = [k for k in ev.keys() if ev[k] is not None]
                    imputed_fields = [
                        'Glucose', 'Blood Pressure', 'BMI', 'Oxygen Saturation', 'LengthOfStay', 'Cholesterol', 'Triglycerides',
                        'Smoking', 'Alcohol', 'Physical Activity', 'Diet Score', 'Family History',
                        'Stress Level', 'Sleep Hours'
                    ]
                    imputed_missing = [k for k in imputed_fields if k not in ev]
                    
                    st.markdown(f"""
                    <div style="background:var(--surface); border:1px solid var(--glass-border); border-left:4px solid var(--accent); border-radius:8px; padding:0.9rem 1.1rem; margin-bottom:1.25rem;">
                        <h5 style="margin:0 0 4px 0; color:var(--accent); font-family:var(--font-h2); font-size:0.95rem;">📄 Medical PDF Extraction Summary</h5>
                        <p style="margin:0 0 4px 0; font-size:0.86rem; color:var(--t1); font-family:var(--font-body);">
                            <b>Directly Extracted from PDF ({len(extracted_fields)} fields):</b> {", ".join(extracted_fields) if extracted_fields else "None"}
                        </p>
                        <p style="margin:0; font-size:0.82rem; color:var(--t3); font-family:var(--font-body);">
                            <b>Absent from PDF (Population Medians Imputed):</b> {", ".join(imputed_missing) if imputed_missing else "None"}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                p_hash = st.session_state.get('target_ipfs_hash_for_analysis', 'manual')
                with col_a:
                    age = st.number_input("Age (Years)", 0, 120, int(ev.get("Age", 45)), key=f"age_{p_hash}")
                    gender = st.selectbox("Biological Gender", ["Male", "Female"], index=0 if ev.get("Gender", "Male") == "Male" else 1, key=f"gen_{p_hash}")
                    glucose = st.number_input("Fasting Glucose Level (mg/dL)", 20.0, 1000.0, float(ev.get("Glucose", 100.0)), key=f"glu_{p_hash}")
                    bp = st.number_input("Systolic Blood Pressure (mm Hg)", 30.0, 300.0, float(ev.get("Blood Pressure", 120.0)), key=f"bp_{p_hash}")
                    bmi = st.number_input("Body Mass Index (BMI)", 10.0, 100.0, float(ev.get("BMI", 24.5)), format="%.2f", key=f"bmi_{p_hash}")
                    oxygen = st.number_input("Oxygen Saturation Level (%)", 0.0, 100.0, float(ev.get("Oxygen Saturation", 98.2)), format="%.1f", key=f"oxy_{p_hash}")
                    stay = st.number_input("Hospital Length of Stay (Days)", 0, 365, int(ev.get("LengthOfStay", 3)), key=f"stay_{p_hash}")
                    chol = st.number_input("Total Serum Cholesterol (mg/dL)", 50.0, 1000.0, float(ev.get("Cholesterol", 190.0)), key=f"chol_{p_hash}")
                    trig = st.number_input("Triglycerides Level (mg/dL)", 20.0, 2000.0, float(ev.get("Triglycerides", 150.0)), key=f"trig_{p_hash}")
                with col_b:
                    hba1c = st.number_input("HbA1c Level (%)", 2.0, 20.0, float(ev.get("HbA1c", 5.4)), format="%.2f", key=f"hba1c_{p_hash}")
                    smoking = st.selectbox("Current Tobacco Smoker?", ["No", "Yes"], index=1 if ev.get("Smoking", 0) == 1 else 0, key=f"smo_{p_hash}")
                    alcohol = st.selectbox("Frequent Alcohol Consumer?", ["No", "Yes"], index=1 if ev.get("Alcohol", 0) == 1 else 0, key=f"alc_{p_hash}")
                    active_hours = st.slider("Weekly Physical Activity (Hours)", 0.0, 25.0, float(ev.get("Physical Activity", 4.5)), 0.5, key=f"act_{p_hash}")
                    diet_score = st.slider("Dietary Score (0 = Poor, 10 = Ideal)", 0.0, 10.0, float(ev.get("Diet Score", 6.5)), 0.5, key=f"diet_{p_hash}")
                    fam_history = st.selectbox("Family History of Disease?", ["No", "Yes"], index=1 if ev.get("Family History", 0) == 1 else 0, key=f"fam_{p_hash}")
                    stress = st.slider("Subjective Stress Level (0 - 10)", 0.0, 10.0, float(ev.get("Stress Level", 4.0)), 0.5, key=f"str_{p_hash}")
                    sleep = st.slider("Daily Sleep Hours", 0.0, 24.0, float(ev.get("Sleep Hours", 7.5)), 0.5, key=f"slp_{p_hash}")
                
                st.markdown("<br/>", unsafe_allow_html=True)
                run_btn = st.form_submit_button("Run Diagnostics & Analysis →", type="primary", use_container_width=True)

            if run_btn:
                # Field-Touch Tracking & Imputation Routing
                defaults_baseline = {
                    "Age": 45, "Glucose": 100.0, "Blood Pressure": 120.0, "BMI": 24.5,
                    "Oxygen Saturation": 98.2, "LengthOfStay": 3, "Cholesterol": 190.0,
                    "Triglycerides": 150.0, "HbA1c": 5.4, "Physical Activity": 4.5,
                    "Diet Score": 6.5, "Stress Level": 4.0, "Sleep Hours": 7.5
                }
                
                raw_vitals = {
                    "Age": age, "Gender": gender, "Glucose": glucose, "Blood Pressure": bp,
                    "BMI": bmi, "Oxygen Saturation": oxygen, "LengthOfStay": stay,
                    "Cholesterol": chol, "Triglycerides": trig, "HbA1c": hba1c,
                    "Smoking": 1 if smoking == "Yes" else 0, "Alcohol": 1 if alcohol == "Yes" else 0,
                    "Physical Activity": active_hours, "Diet Score": diet_score,
                    "Family History": 1 if fam_history == "Yes" else 0,
                    "Stress Level": stress, "Sleep Hours": sleep
                }

                # Block submission if form is 100% untouched baseline defaults and no PDF was extracted
                is_untouched = not has_extracted and all(raw_vitals.get(k) == v for k, v in defaults_baseline.items())
                
                if is_untouched:
                    st.warning("⚠️ Submission Blocked: Form vitals are currently set to un-reviewed default placeholders. Please adjust patient vitals or extract from a PDF report before running AI diagnostics.")
                else:
                    # Construct sanitized vitals: If field was not in PDF and left at form default, set to None for population median imputation
                    vitals = {}
                    for k, val in raw_vitals.items():
                        if val == defaults_baseline.get(k) and (k not in ev):
                            vitals[k] = None
                        else:
                            vitals[k] = val

                    with st.spinner("Analysing clinical data via Random Forest Classifier..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/predict", json={"vitals": vitals}, headers=api_headers())
                            if res.status_code == 200:
                                st.session_state.last_prediction = res.json()
                                st.session_state.patient_vitals = vitals
                                st.session_state.assistant_tab = "📊 Diagnostic Results & SHAP Report"
                                st.rerun()
                            else:
                                try:
                                    err_msg = res.json().get("error", res.text)
                                except Exception:
                                    err_msg = res.text
                                st.error(f"⚠️ Validation / Model Error: {err_msg}")
                        except Exception as e:
                            st.error(f"Cannot communicate with model endpoint: {e}")
            
        elif assist_tab == "📊 Diagnostic Results & SHAP Report":
            st.subheader("Diagnostic Results & SHAP Report")
            if not st.session_state.last_prediction:
                st.info("ℹ️ No diagnostic report generated yet. Fill out the vitals form in the '🩺 Patient Vitals Input & Extraction' tab and click Run Diagnostics.")
            else:
                pred_res = st.session_state.last_prediction
                vitals = st.session_state.patient_vitals
                
                rl = str(pred_res.get("risk_level")).lower()
                badge_class = "badge-low"
                card_border = "var(--glass-border)"
                if "high" in rl:
                    badge_class = "badge-high"
                    card_border = "var(--accent)"
                elif "mod" in rl:
                    badge_class = "badge-moderate"
                    card_border = "var(--accent-sec)"
                else:
                    badge_class = "badge-low"
                    card_border = "var(--glass-border)"
                    
                override_html = ""
                if pred_res.get("overridden"):
                    override_html = f"""
                    <div style="margin-top:0.85rem; padding:0.6rem 0.9rem; background:var(--surface); border:1px solid var(--glass-border); border-radius:6px; font-size:0.82rem; color:var(--t1); font-family:var(--font-body); text-align:left;">
                        💡 <b>Clinical Safety Override Applied:</b> {pred_res.get('override_reason', '')}
                    </div>
                    """

                # 1. HERO DIAGNOSTIC RESULT ELEMENT (Full-Width Primary Focal Point)
                st.markdown(f"""
                <div class="flat-card" style="background:var(--surface); border:1px solid var(--glass-border); border-top: 5px solid {card_border}; border-radius:12px; padding:2rem 2.25rem; box-shadow:0 4px 16px rgba(43,36,32,0.06); text-align:center; margin-bottom:1.5rem;">
                    <div style="font-size:0.78rem; color:var(--t3); font-weight:700; text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-h2);">AI Diagnostic Assessment</div>
                    <div style="font-size:3.2rem; font-weight:400; color:var(--accent); margin:12px 0 6px; font-family:var(--font-h1); letter-spacing:0.04em;">
                        {pred_res.get('prediction')}
                    </div>
                    <div style="display:flex; justify-content:center; align-items:center; gap:16px; margin-top:8px;">
                        <span style="font-size:1.05rem; color:var(--t1); font-family:var(--font-body);">Model Confidence: <b>{pred_res.get('confidence_score'):.1%}</b></span>
                        <span style="color:var(--glass-border);">|</span>
                        <span class="badge {badge_class}" style="font-size:0.85rem; padding:4px 12px;">{pred_res.get('risk_level')} Risk</span>
                    </div>
                    {override_html}
                </div>
                """, unsafe_allow_html=True)
                
                # 1.5 FEATURE PROVENANCE BADGES & WARNINGS
                if pred_res.get("warning"):
                    st.warning(f"⚠️ {pred_res.get('warning')}")
                    
                imputed_list = pred_res.get("imputed_features", [])
                if "extracted_count" in pred_res or imputed_list:
                    st.markdown("##### 🧬 Data Provenance & Reliability")
                    st.markdown("This indicates which fields were explicitly extracted vs. imputed via population medians.")
                    
                    FEATURE_ORDER = [
                        'Age', 'Gender', 'Glucose', 'Blood Pressure', 'BMI', 'Oxygen Saturation', 
                        'LengthOfStay', 'Cholesterol', 'Triglycerides', 'HbA1c', 'Smoking', 'Alcohol', 
                        'Physical Activity', 'Diet Score', 'Family History', 'Stress Level', 'Sleep Hours'
                    ]
                    
                    badge_html = "<div style='display:flex; flex-wrap:wrap; gap:8px; margin-bottom:1.5rem;'>"
                    for feature in FEATURE_ORDER:
                        if feature in imputed_list:
                            badge_html += f"<span style='background:var(--surface); color:var(--high); padding:4px 8px; border-radius:12px; font-size:0.8rem; border:1px solid var(--moderate);'>🟡 {feature}: Estimated</span>"
                        else:
                            badge_html += f"<span style='background:#D1FAE5; color:var(--mint-deep); padding:4px 8px; border-radius:12px; font-size:0.8rem; border:1px solid var(--low);'>🟢 {feature}: Extracted</span>"
                    badge_html += "</div>"
                    st.markdown(badge_html, unsafe_allow_html=True)

                # 2. FULL-WIDTH SUPPORTING EVIDENCE SECTION
                st.markdown("##### 📈 Condition Probability Distributions")
                probs = pred_res.get("probabilities", {})
                if probs:
                    df_probs = pd.DataFrame({
                        "Condition": list(probs.keys()),
                        "Probability": [val * 100 for val in probs.values()]
                    }).sort_values(by="Probability", ascending=True)

                    fig, ax = plt.subplots(figsize=(9.5, 3.8), facecolor='none')
                    ax.set_facecolor('none')

                    conditions = df_probs["Condition"].tolist()
                    values = df_probs["Probability"].tolist()
                    max_v = max(values) if values else 100.0
                    colors = ['#5FC2A8' if v == max_v else '#B3C0F5' for v in values]

                    bars = ax.barh(conditions, values, color=colors, height=0.58)
                    ax.set_xlim(0, max(100.0, max_v + 5))
                    ax.set_xlabel('Probability (%)', color='#223732', fontsize=9.5)
                    ax.tick_params(colors='#223732', labelsize=9.5)
                    ax.xaxis.grid(True, color='#C1D4CE', linestyle='--', linewidth=0.7)
                    ax.set_axisbelow(True)
                    for spine in ax.spines.values():
                        spine.set_color('#E4DDD5')

                    for bar in bars:
                        w = bar.get_width()
                        ax.text(w + 1.2, bar.get_y() + bar.get_height()/2.0, f"{w:.1f}%", va='center', ha='left', color='#223732', fontsize=9)

                    plt.tight_layout()
                    st.pyplot(fig, transparent=True)
                    plt.close(fig)
                    
                if pred_res.get("shap_image"):
                    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
                    st.markdown("##### 🤖 SHAP Feature Impact Breakdown")
                    st.image(f"data:image/png;base64,{pred_res.get('shap_image')}", use_container_width=True)
                    st.caption("SHAP waterfall plot showing positive feature impact (var(--accent)) vs. negative feature impact (var(--t3)).")
                elif pred_res.get("shap_error"):
                    st.warning(f"Could not generate SHAP plot: {pred_res.get('shap_error')}")

                # 3. ORIGINAL UPLOADED PDF REPORT
                if st.session_state.get('target_ipfs_hash_for_analysis'):
                    with st.expander("📄 View Original Uploaded PDF Medical Report", expanded=False):
                        ipfs_hash = st.session_state.target_ipfs_hash_for_analysis
                        st.markdown(f'<iframe src="http://127.0.0.1:8080/ipfs/{ipfs_hash}" width="100%" height="420px" style="border:1px solid var(--glass-border); border-radius:8px;"></iframe>', unsafe_allow_html=True)

                # 4. FOLLOW-UP ACTIONS SECTION (SEPARATED AT THE BOTTOM)
                st.markdown("<hr style='border:none; border-top:1px solid var(--glass-border); margin:2rem 0;'/>", unsafe_allow_html=True)

                st.markdown("""
                <div style="display:flex; align-items:center; margin-bottom:0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                    <h5 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.05rem; font-weight:700;">Preventive Clinical Advisories</h5>
                </div>
                """, unsafe_allow_html=True)
                
                recs = pred_res.get("recommendations", [])
                for r in recs:
                    st.markdown(f"- <span style='font-size:0.92rem; color:var(--t2); font-family:var(--font-body);'>{r}</span>", unsafe_allow_html=True)
                    
                st.markdown("<br/>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style="display:flex; align-items:center; margin-bottom:0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M12 13V2l4 4"/><path d="m12 2-4 4"/><path d="M20 13v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6"/></svg>
                    <h5 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.05rem; font-weight:700;">Commit Diagnostic to Blockchain Ledger</h5>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("commit_ledger_form"):
                    def_patient = st.session_state.get("target_patient_id_for_commit", "")
                    def_ehr = st.session_state.get("target_ehr_id_for_commit", "")
                    
                    target_patient_id = st.text_input("Verify Patient Username ID", value=def_patient, placeholder="e.g. test_patient")
                    target_ehr_id = st.text_input("Target EHR ID to Evaluate (Optional)", value=def_ehr, placeholder="e.g. ehr_1234abcd", help="Enter the ID of an existing manual upload to update it with this AI evaluation.")
                    notes = st.text_area("Physician Diagnostic Observations", placeholder="Enter specific instructions or diagnostics findings...", height=80)
                    commit_btn = st.form_submit_button("Sign & Anchors Record to Fabric →", type="primary", use_container_width=True)
                    
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
                                    st.success("✅ EHR Diagnostic record securely committed to Blockchain ledger!")
                                    st.markdown(f"**EHR ID:** {format_hash_badge(res_data.get('record_id'))}", unsafe_allow_html=True)
                                    st.markdown(f"**IPFS CID:** {format_hash_badge(res_data.get('ipfs_hash'), 10, 6)}", unsafe_allow_html=True)
                                    st.caption("A professional PDF report was automatically generated, pinned to IPFS, and metadata was anchored on-ledger.")
                                    if "doctor_records_cache" in st.session_state:
                                        del st.session_state["doctor_records_cache"]
                                    
                                    try:
                                        pdf_res = requests.get(f"{API_BASE_URL}/download_report/{res_data.get('record_id')}", headers=api_headers())
                                        if pdf_res.status_code == 200:
                                            st.download_button(
                                                label="📥 Download Newly Generated Report PDF",
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
    
    # ── Admin Dashboard Summary
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
                <div class="metric-card-value" style="color:var(--high);">100% ONLINE</div>
                <div class="metric-card-footer">Hyperledger Fabric &amp; IPFS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display:flex; align-items:center; margin-bottom: 1.25rem; margin-top: 1.75rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z"/><path d="M12 22V12"/><path d="m9 15 3-3 3 3"/></svg>
            <h3 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.35rem; font-weight:700;">Global Ledger Audit Trail</h3>
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

    # ── Admin User Directory Page
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
            
            search_u = st.text_input("🔍 Filter Username", "").strip().lower()
            if search_u:
                df_users = df_users[df_users["Username / Node ID"].str.lower().str.contains(search_u)]
                
            st.dataframe(df_users, use_container_width=True)

    # ── Admin Docker & Network Diagnostics Page
    elif "Network Diagnostics" in page:
        st.title("Distributed Infrastructure Diagnostics")
        st.caption("Active container state monitoring for Hyperledger Fabric test-network and IPFS IPFS daemon nodes.")
        
        col_c, col_d = st.columns([5, 3])
        
        with col_c:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom: 1.25rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect width="20" height="8" x="2" y="3" rx="2"/><rect width="20" height="8" x="2" y="13" rx="2"/><line x1="6" x2="6.01" y1="7" y2="7"/><line x1="6" x2="6.01" y1="17" y2="17"/></svg>
                <h3 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.2rem; font-weight:700;">Docker Infrastructure Monitor</h3>
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
                    dot_color = "🟢" if "Up" in status else "🔴"
                    st.markdown(f"""
                    <div class="flat-card" style="padding:0.85rem 1.15rem; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:var(--t1); font-size:0.9rem; font-family:var(--font-h2);">{c.get('name')}</span><br/>
                            <span style="font-size:0.85rem; color:var(--t2); font-family:var(--font-body);">Image: <code>{c.get('image')}</code></span>
                        </div>
                        <span style="font-size:0.8rem; font-weight:600; font-family:var(--font-h2);">{dot_color} {status}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with col_d:
            st.markdown("""
            <div style="display:flex; align-items:center; margin-bottom: 1.25rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--high)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/></svg>
                <h3 style="margin:0; color:var(--t1); font-family:var(--font-h2); font-size:1.2rem; font-weight:700;">Network Gateways &amp; Ports</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="flat-card">
                <div style="font-weight:700; font-size:0.8rem; color:var(--t2); margin-bottom:4px; font-family:var(--font-h2); text-transform:uppercase; letter-spacing:0.04em;">Flask REST Backend</div>
                <div style="font-family:monospace; font-size:0.88rem; color:var(--t1); margin-bottom:12px; font-weight:600;">http://127.0.0.1:5000</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:var(--t2); margin-bottom:4px; font-family:var(--font-h2); text-transform:uppercase; letter-spacing:0.04em;">IPFS API Node Endpoint</div>
                <div style="font-family:monospace; font-size:0.88rem; color:var(--t1); margin-bottom:12px; font-weight:600;">http://127.0.0.1:5001</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:var(--t2); margin-bottom:4px; font-family:var(--font-h2); text-transform:uppercase; letter-spacing:0.04em;">Local IPFS HTTP Gateway</div>
                <div style="font-family:monospace; font-size:0.88rem; color:var(--t1); margin-bottom:12px; font-weight:600;">http://127.0.0.1:8080</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:var(--t2); margin-bottom:4px; font-family:var(--font-h2); text-transform:uppercase; letter-spacing:0.04em;">Fabric Orderer Node</div>
                <div style="font-family:monospace; font-size:0.88rem; color:var(--t1); margin-bottom:12px; font-weight:600;">orderer.example.com:7050</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:var(--t2); margin-bottom:4px; font-family:var(--font-h2); text-transform:uppercase; letter-spacing:0.04em;">Fabric Peer Org1 Node</div>
                <div style="font-family:monospace; font-size:0.88rem; color:var(--t1); margin-bottom:12px; font-weight:600;">peer0.org1.example.com:7051</div>
                
                <div style="font-weight:700; font-size:0.8rem; color:var(--t2); margin-bottom:4px; font-family:var(--font-h2); text-transform:uppercase; letter-spacing:0.04em;">Fabric Peer Org2 Node</div>
                <div style="font-family:monospace; font-size:0.88rem; color:var(--t1); font-weight:600;">peer0.org2.example.com:9051</div>
            </div>
            """, unsafe_allow_html=True)