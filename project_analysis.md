# Complete Project Analysis: HealthChain EHR

## Architecture Overview

**HealthChain EHR** is a secure, decentralized Electronic Health Record (EHR) platform. It uses a modern multi-tier architecture combining web services, Machine Learning (ML), decentralized storage (IPFS), and a permissioned blockchain (Hyperledger Fabric) to ensure patient data is securely stored, accessed, and evaluated.

### Core Objectives
- **Security & Immutability:** Medical documents (files) are hashed and stored on IPFS, while the immutable hash and access lists are preserved on Hyperledger Fabric.
- **Smart Diagnostics:** Doctors can evaluate patient cardiovascular risks using an integrated Machine Learning model.
- **Role-Based Access Control (RBAC):** Strict separation of privileges between `Patients` and `Doctors`. Patients dictate who can view their records.

---

## 🏗 Component Breakdown

The project repository is split into clearly defined micro-components:

### 1. `backend/` (Flask API Server)
The core engine of the system.
- **Role:** Handles authentication, routes ML predictions, forwards files to IPFS, and acts as a bridge to the Hyperledger Fabric blockchain.
- **Tech Stack:** Python (Flask, JWT for Auth, SQLite for User Auth).
- **Key Modules:**
  - `app.py`: Defines REST APIs (`/register`, `/login`, `/upload_record`, `/predict`, `/grant_access`, `/get_records_by_doctor`).
  - `fabric_utils.py`: Contains subprocess wrappers that dynamically inject cryptographic MSP (Membership Service Provider) credentials and execute `docker exec` commands to interact with the Fabric peer (`peer0.org1.example.com`).
  - `db.py`: Simple SQLite user identity management.

### 2. `frontend/` (Streamlit Python Dashboard)
- **Role:** The primary user interface.
- **Tech Stack:** Python (Streamlit).
- **Structure:** `main.py` provides a rich, CSS-styled portal to log in, upload records, grant access (if Patient), or predict heart risk and view records (if Doctor). It makes REST requests to `http://127.0.0.1:5000`.

### 3. `blockchain/` (Hyperledger Fabric Smart Contracts)
- **Role:** The decentralized ledger logic determining data ownership, immutability, and state transitions.
- **Tech Stack:** Golang (`contractapi`).
- **Chaincode (`ehr_contract.go`):** 
  - `CreateRecord`: Establishes a new EHR asset. The creator (Patient) is added to `AuthorizedUsers` by default.
  - `GrantAccess`: Allows pushing a Doctor's ID to the `AuthorizedUsers` array.
  - `GetRecordsByDoctor`: Iterates through the ledger and returns only records where the Doctor's ID is in the `AuthorizedUsers` array.

### 4. `ml/` (Predictive AI Engine)
- **Role:** Provides diagnostic capabilities to Doctors.
- **Pre-trained Models:** Includes `best_model.pkl` (Random Forest model predicting across 7 condition classes), `scaler.pkl`, and SHAP TreeExplainer visualization logic in `predict.py`.

---

## 🚧 Planned / Not Yet Implemented Modules

### `web_frontend/` (Future React Single-Page Application)
- **Status:** **PLANNED / FUTURE WORKMODULE (UNIMPLEMENTED)**
- **Description:** A placeholder Vite + React single-page application structure intended for future web-native interface expansion.
- **Current Operational Interface:** The active production interface is the Streamlit app in `frontend/main.py`. `web_frontend/` contains default boilerplate and is not currently integrated with the backend APIs.


---

## 🔄 How the Workflows Operate (Step-by-Step)

### Workflow 1: User Registration & Authentication
1. User interacts with the UI (Streamlit or React) to **Register**.
2. Flask API hashes the password and saves the `(username, hash, role)` in a local `SQLite` database.
3. User **Logs in**, and Flask issues a **JWT Token** valid for 24 hours. The token encodes the user's explicit role (`doctor` or `patient`).
4. All subsequent API calls require this Bearer Token.

### Workflow 2: Patient Uploads a Medical Record
1. **Patient** logs in, inputs clinical notes, and uploads a medical file.
2. The UI sends a `POST /upload_record` request to Flask.
3. **Decentralized Storage:** Flask relays the raw file to a local IPFS daemon (`http://127.0.0.1:5001/api/v0/add`). IPFS returns a cryptographic hash (CID) representing the file.
4. **Blockchain Anchoring:** Flask calls `fabric_utils.CreateRecord()`. This invokes the Go Smart Contract on the Fabric network, saving a State Object containing:
   `[Record ID, Patient ID, IPFS CID, ML Prediction]`
5. This guarantees the file can never be tampered with (the hash would change) and guarantees the timestamp of upload.

### Workflow 3: Securing & Granting Access
1. By default, **only the Patient** is listed in the `AuthorizedUsers` array on the Fabric Ledger. 
2. Patient navigates to the UI, enters a `Record ID` and a `Doctor's Username`, and clicks **Grant Access**.
3. Flask calls `fabric_utils.GrantAccess()`, which submits an update transaction to the Fabric Smart Contract.
4. The Smart Contract verifies the record exists, appends the doctor's ID, and writes the new state.

### Workflow 4: Doctor Viewing & Diagnostics
1. **Doctor** navigates to the portal.
2. Clicking "Load My Patient Records" fires `GET /get_records_by_doctor`.
3. The Fabric Smart Contract iterates through all ledgers, filtering out any records unless the Doctor's ID is inside the `AuthorizedUsers` list.
4. **AI Diagnostics:** If a Doctor needs to evaluate a patient, they use the ML Prediction tab. They enter 13 physiological metrics (Age, BP, Cholesterol, etc.). Flask scales the data, runs the `heart_model.joblib` inference, and returns either "Low Risk" or "High Risk".

---


---

## 🎯 ML Model Characteristics & Intentional Design Decisions

### 1. Asymmetric Cancer Risk Threshold Policy
- `Cancer` predictions are assigned a **"High Risk"** classification at a calibrated confidence threshold of **$\ge 0.25$** (compared to $\ge 0.40$ for all other conditions: Asthma, Arthritis, Diabetes, Hypertension, Obesity).
- **Clinical Precaution Rationale:** Cancer is a high-stakes, life-threatening condition where a false negative (under-triaging potential malignancy) carries far severe clinical risks than a false positive. Lowering the threshold to 0.25 (just above 14.28% random chance across 7 classes) ensures potential cancer indicators receive immediate clinical review.
- **Asymmetry Check:** No other class utilizes an asymmetric threshold.

### 2. Known Model Limitations & Reliability Boundaries
- **Arthritis Recall Deficit:** `Arthritis` exhibits the lowest recall (**64.35%**) among all 7 target classes due to feature overlap in synthetic data. Predictions for Arthritis should be treated as lower-confidence clinical indicators.
- **Boundary Cutoff Sensitivity:** Patients with vitals sitting 1 point past binary healthy override limits (e.g., Blood Pressure = 121 mmHg vs 120 mmHg cutoff) bypass the `apply_clinical_safety_override` layer and are evaluated directly by the underlying Random Forest model.
