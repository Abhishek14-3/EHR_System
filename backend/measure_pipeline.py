import time
import uuid
import json
import os
import sys

# Ensure backend folder and project root are in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fabric_utils as fu
from report_generator import generate_patient_pdf
import requests

# Dynamically import ml predict logic
from ml.predict import make_prediction

def run_pipeline_measurement():
    print("==============================================================")
    print("      EHR SYSTEM PIPELINE LATENCY PROFILE RUN")
    print("==============================================================")
    
    # 1. Prepare sample payload
    vitals = {
        "Age": 58,
        "Gender": "Male",
        "Glucose": 150,
        "Blood Pressure": 135,
        "BMI": 29.5,
        "Oxygen Saturation": 96.2,
        "LengthOfStay": 4,
        "Cholesterol": 220,
        "Triglycerides": 185,
        "HbA1c": 6.8,
        "Smoking": 0,
        "Alcohol": 1,
        "Physical Activity": 3.0,
        "Diet Score": 7.2,
        "Family History": 0,
        "Stress Level": 5.0,
        "Sleep Hours": 7.0
    }
    patient_id = "patient_profile_test"
    doctor_id = "dr_auditor"
    doctor_notes = "Baseline vitals profile test under normal pipeline audit loads."
    
    # Track timestamps
    timestamps = {}
    
    # Step 1: Start
    t_start = time.perf_counter()
    timestamps['start'] = t_start
    print("t0 [0.00 ms]: Initiating vitals submission...")
    
    # Step 2: ML Inference
    pred_res = make_prediction(vitals)
    t_inference = time.perf_counter()
    timestamps['inference'] = t_inference
    print(f"t1 [{(t_inference - t_start)*1000:.2f} ms]: ML Inference Completed. Condition: {pred_res.get('prediction')}, Confidence: {pred_res.get('confidence_score'):.2%}")
    
    # Step 3: PDF Generation
    pdf_filename = f"report_audit_{uuid.uuid4().hex[:6]}.pdf"
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    generate_patient_pdf(
        patient_id=patient_id,
        doctor_id=doctor_id,
        prediction_data=pred_res,
        patient_vitals=vitals,
        doctor_notes=doctor_notes,
        output_path=pdf_path
    )
    t_pdf = time.perf_counter()
    timestamps['pdf'] = t_pdf
    print(f"t2 [{(t_pdf - t_start)*1000:.2f} ms]: Clinical PDF generated locally.")
    
    # Step 4: IPFS Upload
    with open(pdf_path, 'rb') as f:
        files = {'file': f.read()}
        ipfs_res = requests.post('http://127.0.0.1:5001/api/v0/add', files=files)
        ipfs_res.raise_for_status()
        ipfs_hash = ipfs_res.json()['Hash']
    t_ipfs = time.perf_counter()
    timestamps['ipfs'] = t_ipfs
    print(f"t3 [{(t_ipfs - t_start)*1000:.2f} ms]: PDF uploaded to IPFS. CID: {ipfs_hash}")
    
    # Step 5: Ledger Inscription (CreateRecord)
    prediction_metadata = {
        "prediction": pred_res["prediction"],
        "risk_score": float(pred_res["confidence_score"]),
        "risk_level": pred_res["risk_level"],
        "timestamp": "2026-07-30 07:17:00 UTC",
        "doctor_id": doctor_id,
        "doctor_notes": doctor_notes,
        "type": "prediction"
    }
    
    record_id = f"ehr_audit_{uuid.uuid4().hex[:4]}"
    fabric_res = fu.create_ehr_record(
        record_id=record_id,
        patient_id=patient_id,
        ipfs_hash=ipfs_hash,
        prediction=json.dumps(prediction_metadata)
    )
    t_ledger = time.perf_counter()
    timestamps['ledger'] = t_ledger
    print(f"t4 [{(t_ledger - t_start)*1000:.2f} ms]: Block Committed to Fabric Ledger (CreateRecord success).")
    
    # Step 6: Access Grant (GrantAccess)
    fu.grant_access(record_id, doctor_id)
    t_grant = time.perf_counter()
    timestamps['grant'] = t_grant
    print(f"t5 [{(t_grant - t_start)*1000:.2f} ms]: Doctor access authorization successfully registered.")
    
    # Cleanup temp pdf
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        
    # Print profile summary
    print("\n==============================================================")
    print("                 PIPELINE LATENCY ANALYSIS")
    print("==============================================================")
    dur_ml = (t_inference - t_start) * 1000
    dur_pdf = (t_pdf - t_inference) * 1000
    dur_ipfs = (t_ipfs - t_pdf) * 1000
    dur_ledger = (t_ledger - t_ipfs) * 1000
    dur_grant = (t_grant - t_ledger) * 1000
    dur_total = (t_grant - t_start) * 1000
    
    print(f"1. ML Inference:          {dur_ml:10.2f} ms  ({dur_ml/dur_total:5.1%})")
    print(f"2. PDF Report Compiler:   {dur_pdf:10.2f} ms  ({dur_pdf/dur_total:5.1%})")
    print(f"3. IPFS Upload:           {dur_ipfs:10.2f} ms  ({dur_ipfs/dur_total:5.1%})")
    print(f"4. Fabric CreateRecord:   {dur_ledger:10.2f} ms  ({dur_ledger/dur_total:5.1%})")
    print(f"5. Fabric GrantAccess:    {dur_grant:10.2f} ms  ({dur_grant/dur_total:5.1%})")
    print("-" * 62)
    print(f"Total Pipeline Latency:   {dur_total:10.2f} ms  (100.0%)")
    print("==============================================================")

if __name__ == "__main__":
    run_pipeline_measurement()
