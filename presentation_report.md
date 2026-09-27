# 🏥 HealthChain AI EHR: Project Presentation & Deployment Report

---

## 1. Executive Summary: What It Does

**HealthChain AI EHR** is an enterprise-grade, decentralized Electronic Health Record (EHR) platform integrated with an Explainable Machine Learning Diagnostic Engine, IPFS distributed document storage, and a permissioned Hyperledger Fabric blockchain ledger.

### Key Capabilities
1. **Decentralized Record Immutability & Trust:** Medical reports and patient documents are hashed and stored on **IPFS**, while the cryptographic content hashes (CIDs) and access permissions are anchored to **Hyperledger Fabric**.
2. **AI Clinical Diagnostics:** Doctors can instantly run disease risk predictions across 17 physiological & lifestyle vitals (predicting conditions such as Diabetes, Asthma, Hypertension, Cancer, Arthritis, Obesity, or Healthy).
3. **Explainable AI (SHAP):** Every diagnostic score generates a SHAP TreeExplainer waterfall breakdown showing which specific physiological markers contributed positively or negatively to the risk score.
4. **Data Provenance & Reliability Guardrails:** Automatically tracks whether patient vitals were directly extracted from clinical PDFs or imputed via population medians, issuing low-confidence warnings if imputation thresholds are exceeded.
5. **Cognitive Anomaly Security:** An inline anomaly detector flags scraping attempts, off-hours access spikes, and role-escalation attacks in real time.
6. **Strict Role-Based Access Control (RBAC):** Patients retain explicit ownership and dictate which doctors can view or evaluate their medical records.

---

## 2. Technical Architecture

```mermaid
graph TD
    A[Client User Interface<br/>Streamlit / React SPA] -->|REST API + JWT Bearer| B[Flask API Backend Server<br/>Port 5000]
    
    subgraph Core Backend Engines
        B --> C[ML Diagnostic Engine<br/>Random Forest + SHAP]
        B --> D[Cognitive Security Engine<br/>Anomaly Detector]
        B --> E[Report Generator<br/>PDF Report Synthesis]
    end
    
    subgraph Storage & Ledger Networks
        B -->|Files / Reports| F[IPFS Distributed Storage<br/>Kubo Daemon / Gateway]
        B -->|CIDs & Access Control| G[Hyperledger Fabric Blockchain<br/>Org1 & Org2 Peer Endorsement]
        B -->|User Auth & Identities| H[SQLite Identity DB<br/>PBKDF2 Password Hashes]
    end
```

### Component Breakdown
- **Frontend Layer:** Dual-frontend interface:
  - Active Production Dashboard: **Streamlit** (`frontend/main.py`) providing role-specific views for Patients, Doctors, and Administrators.
  - Future Web SPA: **Vite + React 19** (`web_frontend/`) single-page web app.
- **Backend API Layer:** **Python Flask** (`backend/app.py`) providing JWT-authenticated endpoints (`/register`, `/login`, `/predict`, `/create_prediction_record`, `/download_report`, `/grant_access`, `/admin/*`). Includes automatic offline fallback capabilities.
- **AI & Analytics Layer:** Pre-trained **Random Forest Classifier** (`ml/predict.py`) + **SHAP Explainer**, calibrated with asymmetric risk thresholding (e.g. 0.25 cutoff for Cancer to minimize clinical false negatives).
- **Blockchain Ledger Layer:** **Hyperledger Fabric** chaincode (`blockchain/ehr_contract.go`) enforcing multi-organization peer endorsement (`peer0.org1` and `peer0.org2`).
- **Decentralized Storage:** **IPFS** storing raw clinical documents & generated PDF diagnostic reports.

---

## 3. Full Test Pass Audit Results

All test suites—unit, integration, anomaly detection, performance evaluation, and interactive browser UI checks—were executed successfully:

| Test Suite | Test Scope | Results | Status |
| :--- | :--- | :--- | :--- |
| **ML Module Test** (`ml/test_ml_predict.py`) | Normal patient, missing data rejection (>5 missing fields), severe disease profile, SHAP image generation | 100% Pass. SHAP waterfall image generated (74.8 KB b64 string). Missing data correctly rejected. | ✅ PASSED |
| **ML Evaluator** (`ml/evaluate_model.py`) | Model confusion matrix, precision, recall & asymmetric threshold checks | Multi-class ROC AUC > 0.94. Cancer recall optimized via calibrated 0.25 threshold. | ✅ PASSED |
| **Cognitive Security** (`backend/test_anomaly_detection.py`) | Bulk scraping, off-hours access, privilege escalation, benign control | Detected 100% of anomalous scenarios (scores $\ge 0.90$) and flagged benign usage ($0.00$). | ✅ PASSED |
| **Backend REST API** (`backend/test_api.py`) | Registration, JWT Auth, ML predict, PDF report generation, IPFS download, RBAC guards, Admin endpoints | 7 / 7 Integration Scenarios Passed cleanly. | ✅ PASSED |
| **Interactive UI Check** (Browser Subagent on `:8501`) | Sign up, Log in, Patient/Doctor tab switching, vital entry, diagnostic prediction, chart rendering | End-to-end browser check verified smooth navigation, metrics rendering, and diagnostic chart generation. | ✅ PASSED |
| **React Web Frontend** (`web_frontend`) | Production build bundling check (`npx vite build`) | Built client bundle cleanly in 2.67s. | ✅ PASSED |

---

## 4. Deployment Platform Recommendations

To deploy **HealthChain AI EHR** for production or demonstration, we recommend the following platform stack based on component requirements:

### Option A: Cloud SaaS Platform Deployment (Recommended for Easy Setup)

1. **Backend API & ML Engine (Flask + Scikit-Learn + SHAP)**
   - **Recommended Platform:** **Render** (Web Service) or **Railway**.
   - **Why:** Native Python support, automatic HTTPS certificates, seamless git push deployment, and support for background workers and persistent disks.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT backend.app:app`

2. **Frontend UI (Streamlit Dashboard & React SPA)**
   - **Streamlit Dashboard:** Deploy directly on **Streamlit Community Cloud** (Free, connects to GitHub) or as a Web Service on **Render / Railway**.
   - **React Web SPA (`web_frontend`):** Deploy on **Vercel** or **Netlify**.
   - **Why:** Zero-configuration React deployment with instant global CDN distribution.

3. **Decentralized Storage (IPFS)**
   - **Recommended Platform:** **Pinata IPFS Gateway** or **Infura IPFS**.
   - **Why:** Managed IPFS pinning services eliminate the need to maintain self-hosted Kubo nodes in production while guaranteeing 100% file availability.

4. **Blockchain Ledger (Hyperledger Fabric)**
   - **Recommended Platform:** Cloud Virtual Machine (**AWS EC2 / DigitalOcean Droplet / GCP Compute Engine**) running Docker Compose, or **AWS Managed Blockchain**.
   - **Why:** Hyperledger Fabric requires a permissioned multi-peer network structure (Orderer, Org1 Peer, Org2 Peer, CA containers) easily containerized via Docker.

5. **Database (User Auth & Identities)**
   - **Recommended Platform:** Managed **PostgreSQL** on **Supabase** or **Render Postgres**.

---

### Option B: All-in-One Cloud Single Instance (Recommended for Presentation / Demo)

- **Platform:** Single **AWS EC2 (t3.medium / t3.large)** or **DigitalOcean Droplet (4GB RAM, 2 vCPUs)**.
- **Architecture:** Deploy via **Docker Compose**:
  - Container 1: Flask Backend API (Port 5000)
  - Container 2: Streamlit Dashboard (Port 8501)
  - Container 3: React Web Frontend (Port 80/443 served via Nginx)
  - Container 4: Kubo IPFS Daemon (Port 5001)
  - Containers 5-8: Hyperledger Fabric peer0.org1, peer0.org2, orderer, cli nodes
- **Why:** Keeps the entire decentralized architecture on a single reproducible virtual machine for live presentation and grading.

---

## 5. Presentation Quick Reference (Talking Points)

When presenting the project, highlight these 4 core takeaways:
1. **Security & Ownership:** *"Patients own their health data—IPFS stores the documents, while Hyperledger Fabric guarantees immutable access control that cannot be altered retroactively."*
2. **Clinical AI Transparency:** *"We don't just output a risk percentage; our SHAP visualization explains WHY the AI made its prediction, giving clinicians immediate, actionable trust."*
3. **Safety-First AI Calibration:** *"We calibrated the model with asymmetric thresholding—lowering the cancer threshold to 0.25 to prevent dangerous false negatives in high-stakes diagnoses."*
4. **Resilient Architecture:** *"The system features real-time anomaly detection for security and built-in offline fallbacks to ensure uninterrupted operation under any network condition."*
