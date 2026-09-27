"""
Applies Ink & Signal redesign to the login portion of main.py
"""
import os

with open('frontend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('# AUTH PORTAL (LOGIN / REGISTER)')
end_idx = text.find('# MAIN NAVIGATION (Replaced Sidebar)')

# We will construct the new Auth Portal string
NEW_AUTH_PORTAL = """# AUTH PORTAL (LOGIN / REGISTER)
# ==========================================

if 'token' not in st.session_state:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg: #F2EFE8;
    --surface: #FFFFFF;
    --ink: #0D1B1E;
    --ink-soft: #4A5A5E;
    --line: #DAD5C9;
    --signal: #19C39A;
    --pulse: #FF5A3C;
    
    --font-h1: 'Instrument Serif', serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

html, body, .stApp { background-color: var(--bg) !important; color: var(--ink) !important; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; min-width: 100% !important; }
div[data-testid="stVerticalBlock"] > div.element-container:first-child { display: none !important; }

/* Flex row setup */
div[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch !important; margin: 0; min-height: 100vh; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; }

/* Left Panel */
div[data-testid="column"]:first-child {
    background-color: var(--ink);
    background-image: radial-gradient(var(--ink-soft) 1px, transparent 1px);
    background-size: 24px 24px;
    background-position: 0 0;
    padding: 0 8%;
}

/* Right Panel */
div[data-testid="column"]:last-child {
    background-color: var(--bg);
    padding: 0 10%;
}

/* Animations */
.auth-anim {
    animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

/* Brand Panel Internals */
.brand-title { font-family: var(--font-h1); font-size: 3.8rem; font-weight: normal; color: var(--surface); margin: 0 0 12px 0; line-height: 1.05; letter-spacing: -0.01em; }
.brand-desc { font-family: var(--font-body); font-size: 1.05rem; line-height: 1.6; color: rgba(255,255,255,0.7); max-width: 480px; margin-top: 0; margin-bottom: 2.5rem; }
.brand-feat { display: flex; align-items: center; gap: 14px; font-family: var(--font-body); font-size: 0.95rem; color: rgba(255,255,255,0.85); margin-bottom: 1.25rem; }
.brand-feat svg { flex-shrink: 0; stroke: var(--signal); }
.status-chip { display: inline-flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; border: 1px solid var(--ink-soft); padding: 4px 12px; border-radius: 99px; color: var(--signal); width: fit-content; margin-top: 3rem; }

/* Animation Chain */
.ecg-chain { margin: 2.5rem 0; opacity: 0.9; }
.ecg-line { stroke: var(--signal); stroke-width: 1.5; stroke-dasharray: 200; stroke-dashoffset: 200; animation: trace 4s infinite ease-out; }
@keyframes trace { 0% { stroke-dashoffset: 200; } 40%, 100% { stroke-dashoffset: 0; } }

/* Right Panel Overrides */
.form-title { font-family: var(--font-h1); font-size: 2.8rem; font-weight: normal; margin: 0 0 8px 0; color: var(--ink); line-height: 1; letter-spacing: -0.01em; }
.form-subtitle { font-family: var(--font-body); font-size: 1rem; color: var(--ink-soft); margin-top: 0; margin-bottom: 2.5rem; }

/* Form Elements */
[data-testid="stForm"] { border: none !important; background: transparent !important; padding: 0 !important; box-shadow: none !important; }
div[data-baseweb="input"] { background-color: var(--surface) !important; border: 1px solid var(--line) !important; border-radius: 12px !important; height: 48px; box-shadow: none !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within > div:first-child { border-color: var(--signal) !important; box-shadow: 0 0 0 2px rgba(25,195,154,0.15) !important; }
.stTextInput input, .stNumberInput input { font-family: var(--font-body) !important; font-size: 1rem !important; color: var(--ink) !important; height: 48px !important; }
.stTextInput input::placeholder { color: var(--line) !important; text-shadow: none !important; }
[data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p { font-family: var(--font-mono) !important; font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 0.04em !important; color: var(--ink-soft) !important; }

/* Selectbox */
[data-baseweb="select"] > div:first-child { background-color: var(--surface) !important; border: 1px solid var(--line) !important; border-radius: 12px !important; height: 48px; box-shadow: none !important; color: var(--ink) !important; font-family: var(--font-body) !important; font-size: 1rem !important; }

/* Submit Button */
[data-testid="stFormSubmitButton"] button {
    background-color: var(--ink) !important; color: var(--surface) !important; border: none !important; border-radius: 12px !important; height: 48px !important; font-family: var(--font-body) !important; font-size: 0.95rem !important; font-weight: 500 !important; transition: all 0.2s !important; display: flex !important; justify-content: center !important; width: 100% !important; align-items: center !important;
}
[data-testid="stFormSubmitButton"] button:hover { background-color: var(--signal) !important; color: var(--ink) !important; }
[data-testid="stFormSubmitButton"] button::after {
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>');
    margin-left: 8px; vertical-align: middle; transition: transform 0.2s; height: 16px; width: 16px;
}
[data-testid="stFormSubmitButton"] button:hover::after { transform: translateX(4px); }

/* Hide empty alerts */
[data-testid="stAlert"]:has(:empty) { display: none !important; }
[data-testid="stAlert"] { background: transparent; border: 1px solid var(--pulse); border-radius: 8px; padding: 12px; }

/* Pass-reveal button override style */
[data-baseweb="input"] svg { fill: var(--ink-soft) !important; }

/* Toggle Pills */
.pill-container { display: flex; background: var(--line); border-radius: 99px; padding: 4px; width: fit-content; margin-bottom: 2.5rem; gap: 4px; }
div[data-testid="column"]:last-child div.stButton > button {
    border-radius: 99px !important; border: none !important; box-shadow: none !important; padding: 8px 24px !important; height: auto !important;
    font-family: var(--font-mono) !important; font-size: 12px !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; font-weight: 600 !important; transition: all 0.2s !important;
}
div[data-testid="column"]:last-child div.stButton > button[kind="primary"] { background: var(--ink) !important; color: var(--surface) !important; }
div[data-testid="column"]:last-child div.stButton > button[kind="secondary"] { background: transparent !important; color: var(--ink-soft) !important; }
div[data-testid="column"]:last-child div.stButton > button[kind="secondary"]:hover { color: var(--ink) !important; background: rgba(255,255,255,0.4) !important; }

@media (max-width: 900px) {
    div[data-testid="stHorizontalBlock"] { flex-direction: column !important; min-height: unset; }
    div[data-testid="column"]:first-child { height: 120px; min-height: 120px; padding: 1.5rem; justify-content: center; }
    .brand-desc, .brand-feat, .ecg-chain, .status-chip { display: none !important; }
    .brand-title { font-size: 2.2rem; }
    div[data-testid="column"]:last-child { padding: 3rem 1.5rem; }
}
</style>
''', unsafe_allow_html=True)
    
    col_brand, col_form = st.columns([1.2, 1], gap="small")
    
    with col_brand:
        st.markdown('''
<div class="auth-anim">
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--signal)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 1.5rem;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
<h1 class="brand-title">HealthChain AI</h1>
<p class="brand-desc">Enterprise-grade clinical EHR powered by Scikit-Learn ML, Hyperledger Fabric smart contracts, and IPFS distributed storage.</p>
            
<div class="brand-feat">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                Patient-controlled permissions via Smart Contracts
</div>
<div class="brand-feat">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                Automated Gradient Boosting predictive analysis
</div>
<div class="brand-feat">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" x2="12" y1="22.08" y2="12"/></svg>
                Immutable medical file hosting on IPFS node networks
</div>
            
<svg class="ecg-chain" width="200" height="40" viewBox="0 0 200 40">
                <rect x="0" y="10" width="20" height="20" rx="4" fill="none" stroke="var(--ink-soft)" stroke-width="1.5" />
                <rect x="40" y="10" width="20" height="20" rx="4" fill="none" stroke="var(--ink-soft)" stroke-width="1.5" />
                <rect x="80" y="10" width="20" height="20" rx="4" fill="none" stroke="var(--ink-soft)" stroke-width="1.5" />
                <rect x="120" y="10" width="20" height="20" rx="4" fill="none" stroke="var(--ink-soft)" stroke-width="1.5" />
                <path class="ecg-line" d="M -10 20 L 15 20 L 25 5 L 35 35 L 45 10 L 55 20 L 210 20" fill="none" />
</svg>
            
<div class="status-chip">● FABRIC · IPFS · ML</div>
</div>
        ''', unsafe_allow_html=True)
        
    with col_form:
        st.markdown('<div class="auth-anim">', unsafe_allow_html=True)
        
        # Pill container fake wrapper via CSS sibling logic. 
        # But we do st.columns natively so buttons wire up.
        st.markdown('<div class="pill-container">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        if 'reg_success' in st.session_state:
            st.success(st.session_state.reg_success)
            del st.session_state.reg_success

        if st.session_state.auth_mode == "login":
            st.markdown('''
                <h2 class="form-title">Portal Access</h2>
                <p class="form-subtitle">Log in to authenticate your node keys</p>
            ''', unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username Identifier", placeholder="e.g. doctor_smith")
                password = st.text_input("Security Key / Password", type="password", placeholder="••••••••")
                login_submit = st.form_submit_button("Authenticate Identity", type="primary", use_container_width=True)
                
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
            st.markdown('''
                <h2 class="form-title">Node Registration</h2>
                <p class="form-subtitle">Register a new participant on the network</p>
            ''', unsafe_allow_html=True)

            with st.form("register_form"):
                new_username = st.text_input("Choose Username Identifier", placeholder="e.g. patient_doe")
                new_password = st.text_input("Choose Secure Password", type="password", placeholder="••••••••")
                role = st.selectbox("Assign System Role", ["patient", "doctor", "admin"])
                register_submit = st.form_submit_button("Create Identity Ledger Key", type="primary", use_container_width=True)
                
            if register_submit:
                if not new_username or not new_password:
                    st.error("Fields cannot be empty.")
                else:
                    with st.spinner("Registering node identity..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/register", json={"username": new_username, "password": new_password, "role": role})
                            if res.status_code == 201:
                                st.session_state.reg_success = f"Node identity '{new_username}' registered successfully! Please log in."
                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error(res.json().get('message', 'Registration rejected.'))
                        except Exception as e:
                            st.error(f"Failed to connect to Flask API server. {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()
"""

# Reconstruct main
new_text = text[:start_idx] + NEW_AUTH_PORTAL + text[end_idx:]

with open('frontend/main.py', 'w', encoding='utf-8') as f:
    f.write(new_text)
print("Auth portal update successful.")
