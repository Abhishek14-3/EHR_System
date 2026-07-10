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

### 3. `web_frontend/` (Modern React/Vite SPA - Optional/Future)
- **Role:** A modern web UI potentially serving as a sleeker alternative to the Streamlit app.
- **Tech Stack:** Node.js, React, Vite, Tailwind/CSS.

### 4. `blockchain/` (Hyperledger Fabric Smart Contracts)
- **Role:** The decentralized ledger logic determining data ownership, immutability, and state transitions.
- **Tech Stack:** Golang (`contractapi`).
- **Chaincode (`ehr_contract.go`):** 
  - `CreateRecord`: Establishes a new EHR asset. The creator (Patient) is added to `AuthorizedUsers` by default.
  - `GrantAccess`: Allows pushing a Doctor's ID to the `AuthorizedUsers` array.
  - `GetRecordsByDoctor`: Iterates through the ledger and returns only records where the Doctor's ID is in the `AuthorizedUsers` array.

### 5. `ml_model/` (Predictive AI)
- **Role:** Provides diagnostic capabilities to Doctors.
- **Pre-trained Models:** Includes `heart_model.joblib` (a binary classification model predicting presence of heart disease) and `scaler.joblib` (for normalizing the 13 clinical vitals inputted by the doctor).

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

## 🔐 Security & Flaw Analysis

**Strengths:**
- **Decentralization:** Raw files are kept off the blockchain (preventing ledger bloat), utilizing IPFS for sheer storage efficiency, while Fabric ensures governance.
- **Immutability:** Hyperledger Fabric is enterprise-grade. Data access is baked directly into the Go Chaincode logic natively.
- **Authentication:** Standard JWT-based middleware ensures state-less scaling for the Flask backend.

**Areas Configured for "Test Environment":**
- `CLI_CONTAINER / MSP Overrides`: The `fabric_utils.py` currently forces the identity of `User1@org1.example.com` for *all* blockchain transactions, regardless of who is logged into Flask. In a pure production environment, Hyperledger Fabric CA would generate unique certificates for *each* individual patient and doctor.
- IPFS is running on a local node `127.0.0.1:5001`. In production, you'd likely pin to persistent peers like Pinata or Infura.
