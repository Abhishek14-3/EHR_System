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
