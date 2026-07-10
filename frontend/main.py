import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="HealthChain | EHR Dashboard", page_icon="⚕️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

    /* ── CSS Variables ─────────────────────────────────────── */
    :root {
        --navy-950: #F8FAFC;
        --navy-900: #F1F5F9;
        --navy-800: #E2E8F0;
        --navy-700: #CBD5E1;
        --slate-600: #94A3B8;
        --slate-400: #64748B;
        --slate-300: #475569;
        --slate-200: #334155;
        --slate-100: #1E293B;
        --slate-050: #0F172A;
        --accent-cyan: #2563EB;
        --accent-teal: #1D4ED8;
        --accent-glow: rgba(37, 99, 235, 0.10);
        --accent-green: #059669;
        --accent-red:   #DC2626;
        --text-primary: #1E293B;
        --text-secondary: #475569;
        --text-muted: #64748B;
        --border: #E2E8F0;
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 20px;
        --radius-pill: 999px;
        --shadow-card: 0 1px 4px rgba(15, 23, 42, 0.06), 0 0 0 1px rgba(15, 23, 42, 0.04);
        --shadow-glow: 0 2px 8px rgba(37, 99, 235, 0.08);
    }

    /* ── Global Reset ──────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--text-primary);
    }
    .stApp {
        background: #F8FAFC;
        min-height: 100vh;
    }
    .block-container { padding: 0.5rem 2.5rem 3rem; max-width: 1400px; }
    h1, h2, h3, h4 { font-family: 'Syne', sans-serif; }
    a { color: var(--accent-cyan); }

    /* ── Scrollbar ─────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #F1F5F9; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

    /* ── Hide Streamlit chrome ─────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ══════════════════════════════════════════════════════════
       AUTH PORTAL
    ══════════════════════════════════════════════════════════ */
    .auth-outer {
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding: 1rem 2rem 2rem;
    }
    .auth-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: var(--radius-lg);
        padding: 3rem 2.5rem;
        width: 100%;
        max-width: 460px;
        margin: 0 auto;
        box-shadow: 0 2px 12px rgba(15, 23, 42, 0.07);
        position: relative;
        overflow: hidden;
    }
    .auth-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2563EB, #3B82F6);
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        pointer-events: none;
    }
    .auth-logo-ring {
        width: 72px; height: 72px;
        border-radius: 50%;
        background: #EFF6FF;
        border: 1.5px solid #BFDBFE;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 1.25rem;
        font-size: 2rem;
    }
    .auth-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.75rem;
        font-weight: 800;
        text-align: center;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }
    .auth-subtitle {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-bottom: 2rem;
        font-weight: 400;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* ── Radio override for auth tabs ──────────────────────── */
    div[data-testid="stHorizontalBlock"] .stRadio label,
    .stRadio label { color: var(--text-secondary) !important; font-family: 'DM Sans', sans-serif; }
    .stRadio [data-baseweb="radio"] { gap: 0.5rem; }

    /* ── Inputs ────────────────────────────────────────────── */
    .stTextInput input, .stNumberInput input, .stSelectbox select,
    div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 0.6rem 0.875rem !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.10) !important;
        outline: none !important;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stFileUploader label { color: var(--text-secondary) !important; font-size: 0.82rem !important; font-weight: 600 !important; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 4px !important; }

    /* ── Buttons ───────────────────────────────────────────── */
    div[data-testid="stFormSubmitButton"] > button,
    .stButton > button {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.65rem 1.75rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    /* Primary / submit */
    div[data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.25) !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #1D4ED8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.30) !important;
    }
    /* Regular buttons */
    .stButton > button {
        background: #FFFFFF !important;
        color: #2563EB !important;
        border: 1px solid #BFDBFE !important;
    }
    .stButton > button:hover {
        background: #EFF6FF !important;
        border-color: #93C5FD !important;
        transform: translateY(-1px) !important;
    }
    /* Primary type button */
    button[kind="primary"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.20) !important;
    }
    button[kind="primary"]:hover {
        background: #1D4ED8 !important;
    }
    /* Logout danger */
    .logout-btn button {
        background: #FEF2F2 !important;
        color: #DC2626 !important;
        border: 1px solid #FECACA !important;
    }
    .logout-btn button:hover {
        background: #FEE2E2 !important;
        border-color: #FCA5A5 !important;
    }

    /* ── File uploader ─────────────────────────────────────── */
    .stFileUploader > div {
        background: #F8FAFC !important;
        border: 1px dashed #CBD5E1 !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
    }

    /* ══════════════════════════════════════════════════════════
       TOP NAV BAR
    ══════════════════════════════════════════════════════════ */
    .topbar {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0;
    }
    .topbar-logo {
        width: 44px; height: 44px;
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
    }
    .topbar-wordmark {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.03em;
    }
    .topbar-wordmark span { color: var(--accent-cyan); }
    .user-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: var(--radius-pill);
        padding: 6px 16px 6px 10px;
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .user-badge .role-chip {
        background: #EFF6FF;
        color: #2563EB;
        border-radius: var(--radius-pill);
        padding: 2px 8px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        font-family: 'Syne', sans-serif;
    }

    /* ── Divider ───────────────────────────────────────────── */
    hr { border-color: #E2E8F0 !important; margin: 1.25rem 0 !important; }

    /* ══════════════════════════════════════════════════════════
       TABS
    ══════════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: #F1F5F9 !important;
        border-radius: var(--radius-pill) !important;
        padding: 4px !important;
        border: 1px solid #E2E8F0 !important;
        gap: 4px !important;
        display: inline-flex !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: var(--radius-pill) !important;
        color: var(--text-muted) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.04em !important;
        padding: 8px 20px !important;
        transition: all 0.2s !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }
    .stTabPanel { padding-top: 1.5rem !important; }

    /* ══════════════════════════════════════════════════════════
       SECTION HEADERS
    ══════════════════════════════════════════════════════════ */
    .section-header {
        margin-bottom: 1.5rem;
    }
    .section-header h3 {
        font-family: 'Syne', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin: 0 0 4px;
    }
    .section-header p {
        color: var(--text-muted);
        font-size: 0.875rem;
        margin: 0;
        font-weight: 400;
    }

    /* ══════════════════════════════════════════════════════════
       CARDS & INFO PANELS
    ══════════════════════════════════════════════════════════ */
    .info-panel {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 3px solid #2563EB;
        border-radius: var(--radius-md);
        padding: 1.25rem 1.5rem;
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    .info-panel strong { color: var(--text-primary); }

    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: var(--radius-md);
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
    }

    /* ── Expander ──────────────────────────────────────────── */
    .stExpander {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: var(--radius-md) !important;
        margin-bottom: 0.75rem !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }
    .stExpander summary {
        color: var(--text-secondary) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.875rem 1.25rem !important;
    }
    .stExpander [data-testid="stExpanderDetails"] {
        padding: 0 1.25rem 1.25rem !important;
    }

    /* ── Alerts ────────────────────────────────────────────── */
    .stSuccess > div {
        background: #F0FDF4 !important;
        border: 1px solid #BBF7D0 !important;
        border-radius: var(--radius-md) !important;
        color: #15803D !important;
    }
    .stError > div {
        background: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
        border-radius: var(--radius-md) !important;
        color: #DC2626 !important;
    }
    .stInfo > div {
        background: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: var(--radius-md) !important;
        color: #1D4ED8 !important;
    }
    .stWarning > div {
        background: #FFFBEB !important;
        border: 1px solid #FDE68A !important;
        border-radius: var(--radius-md) !important;
        color: #92400E !important;
    }

    /* ── Spinner ───────────────────────────────────────────── */
    .stSpinner > div { border-top-color: var(--accent-cyan) !important; }

    /* ── Code / mono ───────────────────────────────────────── */
    code {
        background: #F1F5F9 !important;
        color: #2563EB !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
        font-size: 0.83em !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ── Selectbox dropdown ────────────────────────────────── */
    div[data-baseweb="select"] li {
        background: #FFFFFF !important;
        color: var(--text-primary) !important;
    }
    div[data-baseweb="select"] li:hover {
        background: #F1F5F9 !important;
    }

    /* ── Caption ───────────────────────────────────────────── */
    .stCaption { color: var(--text-muted) !important; font-size: 0.78rem !important; }

    /* ── Number input arrows ───────────────────────────────── */
    .stNumberInput [data-testid="stNumberInputStepDown"],
    .stNumberInput [data-testid="stNumberInputStepUp"] {
        background: #F1F5F9 !important;
        color: #2563EB !important;
        border-color: #CBD5E1 !important;
    }

    /* ── Markdown text ─────────────────────────────────────── */
    .stMarkdown p { color: var(--text-secondary); line-height: 1.7; }

    /* ── Image centering ───────────────────────────────────── */
    .centered-img { display: flex; justify-content: center; padding: 2rem 0; }
    .centered-img img { opacity: 0.65; filter: none; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# AUTHENTICATION LOGIC (LOGIN / REGISTER)
# ==========================================

if 'token' not in st.session_state:

    st.markdown('<div class="auth-outer"><div class="auth-card">', unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-logo-ring">⚕</div>
    <div class="auth-title">HealthChain Portal</div>
    <div class="auth-subtitle">Secure Identity &amp; Access Management</div>
    """, unsafe_allow_html=True)

    auth_mode = st.radio("Authentication Mode", ["Login", "Register"], horizontal=True, label_visibility="collapsed")

    if auth_mode == "Login":
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_submit = st.form_submit_button("Authenticate →")

        if login_submit:
            with st.spinner("Verifying cryptographic credentials…"):
                try:
                    res = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.token    = data['token']
                        st.session_state.role     = data['role']
                        st.session_state.username = data['username']
                        st.rerun()
                    else:
                        st.error(res.json().get('message', 'Login failed — review credentials'))
                except Exception as e:
                    st.error(f"Cannot connect to server API → {e}")
    else:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username", placeholder="e.g. john_doe")
            new_password = st.text_input("Choose Password", type="password")
            role         = st.selectbox("Role", ["patient", "doctor"])
            register_submit = st.form_submit_button("Create Identity →")

        if register_submit:
            with st.spinner("Registering on network…"):
                try:
                    res = requests.post(f"{API_BASE_URL}/register",
                                        json={"username": new_username, "password": new_password, "role": role})
                    if res.status_code == 201:
                        st.success("✅ Account created! Switch to **Login** to continue.")
                    else:
                        st.error(res.json().get('message', 'Registration failed'))
                except Exception as e:
                    st.error(f"Cannot connect to server: {e}")

    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()


# ==========================================
# HELPERS
# ==========================================

def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def trigger_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


# ==========================================
# TOP NAV BAR
# ==========================================

col1, col2, col3 = st.columns([5, 4, 1])

with col1:
    st.markdown("""
    <div class="topbar">
        <div class="topbar-logo">⚕</div>
        <span class="topbar-wordmark">Health<span>Chain</span> EHR</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    uname = st.session_state.username.capitalize()
    role  = st.session_state.role.upper()
    st.markdown(f"""
    <div style="display:flex; justify-content:flex-end; align-items:center; height:100%;">
        <span class="user-badge">
            👤 {uname}
            <span class="role-chip">{role}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("⏻ Exit", key="logout_btn", on_click=trigger_logout):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()


# ==========================================
# ROLE-BASED TABS
# ==========================================

if st.session_state.role == 'patient':
    tab1, tab3 = st.tabs(["📁  Upload Record", "🔐  Access Control"])
elif st.session_state.role == 'doctor':
    tab2, tab3 = st.tabs(["🧬  ML Predictions", "🔐  View / Request Access"])


# ── Patient: Upload ──────────────────────────────────────────
if st.session_state.role == 'patient':
    with tab1:
        col_a, col_b = st.columns([5, 3], gap="large")
        with col_a:
            st.markdown("""
            <div class="section-header">
                <h3>Add New Patient Record</h3>
                <p>Encrypt and anchor a medical record to the distributed ledger.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("upload_form", clear_on_submit=False):
                p_id          = st.text_input("Patient ID", value=st.session_state.username, disabled=True)
                prediction_val = st.text_input("Recent Diagnostic Prediction (Optional)", placeholder="e.g. Healthy")
                uploaded_file  = st.file_uploader("Medical Record File")
                submitted      = st.form_submit_button("Securely Store Record →")

            if submitted and uploaded_file:
                with st.spinner("Encrypting to IPFS and anchoring to Fabric Ledger…"):
                    try:
                        files    = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        data     = {"patient_id": p_id, "prediction": prediction_val or "Not Evaluated"}
                        response = requests.post(f"{API_BASE_URL}/upload_record", files=files, data=data, headers=api_headers())

                        if response.status_code == 200:
                            res_data   = response.json()
                            fabric_res = res_data.get('fabric_response', {})
                            st.success("✅ Record successfully secured on blockchain!")
                            st.info(f"**Ledger Txn ID:** `{fabric_res.get('txn_id', 'N/A')}`")
                            with st.expander("View Full Transaction Details"):
                                st.write(f"**Record ID:** `{res_data.get('record_id')}`")
                                st.write(f"**IPFS Hash (CID):** `{res_data.get('ipfs_hash')}`")
                        else:
                            st.error(f"❌ Transaction rejected: {response.text}")
                    except Exception as e:
                        st.error(f"🚨 Unexpected error: {e}")

        with col_b:
            st.markdown("""
            <div style="padding-top: 3.5rem;">
                <div class="info-panel">
                    <strong>🔒 Encryption Flow</strong><br><br>
                    Your identity is verified via JWT and the payload is pushed to IPFS.
                    The resulting CID hash is permanently inscribed on the <strong>Hyperledger Fabric</strong>
                    blockchain, ensuring strict immutability and auditability.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Doctor: Predict ──────────────────────────────────────────
if st.session_state.role == 'doctor':
    with tab2:
        st.markdown("""
        <div class="section-header">
            <h3>Clinical AI Assistant — Heart Disease Risk</h3>
            <p>Input patient vitals to evaluate cardiovascular risk via the secure backend model.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("predict_form"):
            col1, col2, col3 = st.columns(3, gap="medium")
            with col1:
                age      = st.number_input("Age", 1, 120, 45)
                trestbps = st.number_input("Resting BP (mm Hg)", 50, 250, 120)
                chol     = st.number_input("Serum Cholesterol (mg/dl)", 100, 600, 200)
                restecg  = st.selectbox("Resting ECG (0–2)", [0, 1, 2])
                thal     = st.selectbox("Thalassemia (0–3)", [0, 1, 2, 3])
            with col2:
                sex     = st.selectbox("Sex", [1, 0], format_func=lambda x: "Male" if x == 1 else "Female")
                cp      = st.selectbox("Chest Pain Type (0–3)", [0, 1, 2, 3])
                fbs     = st.selectbox("Fasting Blood Sugar > 120", [1, 0], format_func=lambda x: "True" if x == 1 else "False")
                thalach = st.number_input("Max Heart Rate", 50, 250, 150)
            with col3:
                exang   = st.selectbox("Exercise Induced Angina", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
                oldpeak = st.number_input("ST Depression", 0.0, 10.0, 1.0, 0.1)
                slope   = st.selectbox("ST Slope (0–2)", [0, 1, 2])
                ca      = st.selectbox("Major Vessels (0–4)", [0, 1, 2, 3, 4])

            predict_submit = st.form_submit_button("Run Neural Analysis →")

        if predict_submit:
            features = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
            with st.spinner("Analysing securely via backend model…"):
                try:
                    response = requests.post(f"{API_BASE_URL}/predict", json={"features": features}, headers=api_headers())
                    if response.status_code == 200:
                        prediction = response.json().get('prediction')
                        if "Disease" in prediction:
                            st.error(f"⚠️ **High Risk Diagnostic:** {prediction}")
                        else:
                            st.success(f"✅ **Low Risk Diagnostic:** {prediction}")
                    else:
                        st.error(f"❌ Unauthorised or server error: {response.text}")
                except Exception as e:
                    st.error(f"🚨 Connection failed: {e}")


# ── Shared: Access Control ────────────────────────────────────
with (tab3 if st.session_state.role in ['patient', 'doctor'] else None):
    col_x, col_y = st.columns([3, 2], gap="large")

    with col_x:
        if st.session_state.role == 'patient':
            st.markdown("""
            <div class="section-header">
                <h3>Manage Provider Access</h3>
                <p>Delegate viewing authority of a specific EHR to a medical professional.</p>
            </div>
            """, unsafe_allow_html=True)

            # Show patient's existing records so they can see valid Record IDs
            st.markdown("#### 📋 Your Records on Blockchain")
            try:
                rec_response = requests.get(f"{API_BASE_URL}/get_my_records", headers=api_headers())
                if rec_response.status_code == 200:
                    my_records = rec_response.json()
                    if my_records:
                        record_ids = [r.get('id', 'N/A') for r in my_records]
                        for rec in my_records:
                            with st.expander(f"🗂 Record ID: `{rec.get('id')}` — {rec.get('mlPrediction', 'N/A')}"):
                                st.markdown(f"**Record ID:** `{rec.get('id')}`")
                                st.markdown(f"**IPFS Hash:** `{rec.get('ipfsHash')}`")
                                st.markdown(f"**AI Diagnostics:** `{rec.get('mlPrediction')}`")
                                auth_users = ", ".join(rec.get('authorizedUsers', []))
                                st.caption(f"Currently authorised: {auth_users}")
                    else:
                        st.info("No records found on blockchain for your account. Upload a record first.")
                        record_ids = []
                else:
                    st.warning("Could not fetch your records from blockchain.")
                    record_ids = []
            except Exception as e:
                st.warning(f"Could not load records: {e}")
                record_ids = []

            st.markdown("---")
            st.markdown("#### 🔐 Grant Access to a Doctor")

            with st.form("grant_auth_form"):
                if record_ids:
                    record_id = st.selectbox("Select Your EHR Record ID", record_ids)
                else:
                    record_id = st.text_input("Your EHR Record ID", placeholder="e.g. ehr_1a2b3c4d")
                doctor_id = st.text_input("Doctor Username to Authorise", placeholder="e.g. doctor_smith")
                grant_submit = st.form_submit_button("Grant Immutable Access →")

            if grant_submit and record_id and doctor_id:
                with st.spinner("Submitting authorisation to ledger…"):
                    try:
                        response = requests.post(f"{API_BASE_URL}/grant_access",
                                                 json={"record_id": record_id, "doctor_id": doctor_id},
                                                 headers=api_headers())
                        if response.status_code == 200:
                            st.success(f"✅ Key-sharing transaction successful for Dr. {doctor_id}!")
                        else:
                            st.error(f"❌ Auth failure: {response.text}")
                    except Exception as e:
                        st.error(f"🚨 Connection failed: {e}")

        elif st.session_state.role == 'doctor':
            st.markdown("""
            <div class="section-header">
                <h3>Authorised Clinical Records</h3>
                <p>View immutable data payloads selectively shared with your clinical identity.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Load My Patient Records", type="primary"):
                with st.spinner("Querying Hyperledger Fabric state database…"):
                    try:
                        response = requests.get(f"{API_BASE_URL}/get_records_by_doctor", headers=api_headers())
                        if response.status_code == 200:
                            records = response.json()
                            if not records:
                                st.warning("📭 No records have been securely shared with your account yet.")
                            else:
                                st.success(f"✅ Extracted {len(records)} authorised decentralised records.")
                                for rec in records:
                                    with st.expander(
                                        f"🗂 {rec.get('id', 'N/A')}  ·  Patient: {rec.get('patientId', 'N/A')}",
                                        expanded=True
                                    ):
                                        st.markdown(f"**Ledger Record ID:** `{rec.get('id')}`")
                                        st.markdown(f"**Patient Identity:** `{rec.get('patientId')}`")
                                        st.markdown(f"**AI Diagnostics:** `{rec.get('mlPrediction')}`")
                                        ipfs_cid = rec.get("ipfsHash", "")
                                        if ipfs_cid:
                                            ipfs_gateway = f"http://127.0.0.1:8080/ipfs/{ipfs_cid}"
                                            st.markdown(f"**Raw Payload:** [🔗 Open IPFS File in Browser]({ipfs_gateway})")
                                        auth_users = ", ".join(rec.get('authorizedUsers', []))
                                        st.caption(f"Network-audited observers: {auth_users}")
                        else:
                            st.error(f"❌ Failed to fetch records: {response.text}")
                    except Exception as e:
                        st.error(f"🚨 Connection failed: {e}")

    with col_y:
        st.markdown('<div class="centered-img">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3204/3204094.png", width=180)
        st.markdown('</div>', unsafe_allow_html=True)