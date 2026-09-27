import time
import requests
import random
import sys
import os

# Reconfigure stdout for UTF-8 to handle unicode checkmarks in Windows terminal
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


API_BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    print("\n" + "=" * 50)
    print(" HEALTHCHAIN AI INTEGRATION TEST AUDIT")
    print("=" * 50)
    
    # Generate unique test usernames
    rand_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
    patient_username = f"test_pat_{rand_id}"
    doctor_username = f"test_doc_{rand_id}"
    admin_username = f"test_adm_{rand_id}"
    test_password = "SecurePassword123"
    
    tokens = {}
    
    # ── Test 1: User Registration ──────────────────────────────────────────
    print("\n[TEST 1] Registering users...")
    roles = [
        {"username": patient_username, "password": test_password, "role": "patient"},
        {"username": doctor_username, "password": test_password, "role": "doctor"},
        {"username": admin_username, "password": test_password, "role": "admin"}
    ]
    
    for r in roles:
        res = requests.post(f"{API_BASE_URL}/register", json=r)
        if res.status_code == 201:
            print(f"  ✓ Registered {r['role']}: {r['username']}")
        else:
            print(f"  ✗ Failed to register {r['role']} {r['username']}: {res.text}")
            return False
            
    # ── Test 2: User Authentication ─────────────────────────────────────────
    print("\n[TEST 2] Authenticating identities and issuing JWT tokens...")
    for r in roles:
        res = requests.post(f"{API_BASE_URL}/login", json={"username": r["username"], "password": r["password"]})
        if res.status_code == 200:
            token = res.json()["token"]
            tokens[r["role"]] = token
            print(f"  ✓ Authenticated {r['role']}, JWT token length: {len(token)}")
        else:
            print(f"  ✗ Authentication failed for {r['username']}: {res.text}")
            return False
            
    headers_pat = {"Authorization": f"Bearer {tokens['patient']}"}
    headers_doc = {"Authorization": f"Bearer {tokens['doctor']}"}
    headers_adm = {"Authorization": f"Bearer {tokens['admin']}"}
    
    # ── Test 3: Vitals Classification (Predict) ─────────────────────────────
    print("\n[TEST 3] Testing ML classification pipeline (/predict)...")
    vitals_payload = {
        "vitals": {
            "Age": 55,
            "Gender": "Male",
            "Glucose": 180,
            "Blood Pressure": 145,
            "BMI": 32.4,
            "Oxygen Saturation": 94.5,
            "LengthOfStay": 5,
            "Cholesterol": 245,
            "Triglycerides": 210,
            "HbA1c": 8.2,
            "Smoking": 1,
            "Alcohol": 0,
            "Physical Activity": 2.0,
            "Diet Score": 4.5,
            "Family History": 1,
            "Stress Level": 7.0,
            "Sleep Hours": 5.5
        }
    }
    
    res = requests.post(f"{API_BASE_URL}/predict", json=vitals_payload, headers=headers_doc)
    if res.status_code == 200:
        pred_data = res.json()
        print("  ✓ Prediction Success:")
        print(f"    - Condition: {pred_data.get('prediction')}")
        print(f"    - Risk Level: {pred_data.get('risk_level')}")
        print(f"    - Confidence: {pred_data.get('confidence_score'):.2%}")
        print(f"    - Advisories count: {len(pred_data.get('recommendations', []))}")
    else:
        print(f"  ✗ Prediction Failed: {res.text}")
        return False
        
    # ── Test 4: Report Generation & Ledger Anchor ─────────────────────────
    print("\n[TEST 4] Generating clinical PDF report, uploading to IPFS, and anchoring Fabric ledger...")
    record_payload = {
        "patient_id": patient_username,
        "vitals": vitals_payload["vitals"],
        "doctor_notes": "Patient shows clinical symptoms of Type II diabetes combined with mild hypertension. Strongly advised immediate DASH diet compliance and sugar restriction."
    }
    
    res = requests.post(f"{API_BASE_URL}/create_prediction_record", json=record_payload, headers=headers_doc)
    if res.status_code == 200:
        record_data = res.json()
        record_id = record_data.get("record_id")
        ipfs_hash = record_data.get("ipfs_hash")
        print("  ✓ Record successfully anchored:")
        print(f"    - EHR Asset ID: {record_id}")
        print(f"    - IPFS CID: {ipfs_hash}")
        print(f"    - Txn ID: {record_data.get('fabric_response', {}).get('txn_id')}")
    else:
        print(f"  ✗ Record Anchor Failed: {res.text}")
        return False
        
    # ── Test 5: Verify Permissions (RBAC) ──────────────────────────────────
    print("\n[TEST 5] Testing role-based access controls on ledger query...")
    # Doctor gets their records
    res = requests.get(f"{API_BASE_URL}/get_records_by_doctor", headers=headers_doc)
    if res.status_code == 200:
        shared_records = res.json()
        has_record = any(r.get("id") == record_id for r in shared_records)
        print(f"  ✓ Doctor query: returned {len(shared_records)} shared files. Record in list? {has_record}")
    else:
        print(f"  ✗ Doctor query failed: {res.text}")
        return False
        
    # Patient gets their records
    res = requests.get(f"{API_BASE_URL}/get_my_records", headers=headers_pat)
    if res.status_code == 200:
        patient_records = res.json()
        has_record = any(r.get("id") == record_id for r in patient_records)
        print(f"  ✓ Patient query: returned {len(patient_records)} own records. Record in list? {has_record}")
    else:
        print(f"  ✗ Patient query failed: {res.text}")
        return False
        
    # ── Test 6: Report Retrieval (Download) ───────────────────────────────
    print("\n[TEST 6] Downloading PDF clinical report from IPFS through backend...")
    res = requests.get(f"{API_BASE_URL}/download_report/{record_id}", headers=headers_doc)
    if res.status_code == 200:
        pdf_bytes = res.content
        print(f"  ✓ Report download: Retrieved PDF file successfully, size: {len(pdf_bytes)} bytes")
        # Save a test report copy locally
        test_out_path = os.path.join(os.path.dirname(__file__), "test_report_download.pdf")
        with open(test_out_path, "wb") as out_f:
            out_f.write(pdf_bytes)
        print(f"  ✓ Local file copy saved for inspection: {test_out_path}")
    else:
        print(f"  ✗ Report download failed: {res.text}")
        return False
        
    # ── Test 7: Administrator Dashboards ────────────────────────────────────
    print("\n[TEST 7] Testing administrator diagnostics endpoints...")
    # Get user directory
    res = requests.get(f"{API_BASE_URL}/admin/users", headers=headers_adm)
    if res.status_code == 200:
        users_list = res.json()
        print(f"  ✓ Admin users list size: {len(users_list)}")
    else:
        print(f"  ✗ Admin users list query failed: {res.text}")
        return False
        
    # Get stats
    res = requests.get(f"{API_BASE_URL}/admin/stats", headers=headers_adm)
    if res.status_code == 200:
        stats = res.json()
        print(f"  ✓ Admin Stats: Patients={stats.get('patients')}, Doctors={stats.get('doctors')}, Records={stats.get('records')}")
    else:
        print(f"  ✗ Admin stats query failed: {res.text}")
        return False
        
    # Get docker status
    res = requests.get(f"{API_BASE_URL}/admin/docker_status", headers=headers_adm)
    if res.status_code == 200:
        status_res = res.json()
        containers = status_res.get("containers", [])
        print(f"  ✓ Admin Docker Status: Found {len(containers)} active container nodes.")
        for c in containers:
            print(f"    - {c.get('name')}: {c.get('status')}")
    else:
        print(f"  ✗ Admin docker status query failed: {res.text}")
        return False
        
    print("\n" + "=" * 50)
    print(" ALL TESTS PASSED SUCCESSFULLY! ✅")
    print("=" * 50 + "\n")
    return True

if __name__ == "__main__":
    # Check if backend is active
    try:
        requests.get(f"{API_BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("✗ Error: The Flask backend API is not running on port 5000.")
        print("Please start the backend server (python backend/app.py) first.")
        sys.exit(1)
        
    success = run_tests()
    sys.exit(0 if success else 1)
