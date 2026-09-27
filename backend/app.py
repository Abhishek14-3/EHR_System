from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
import sys
import datetime
from datetime import timezone
from functools import wraps
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import pdfplumber
import re
import io

import hashlib

import db
import fabric_utils

# ==========================================
# INITIAL SETUP & PATH RESOLUTION
# ==========================================

# Initialize Database
db.init_db()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c5c645e5b3ee0b89f8121fc09440bf5e22ea1f681a96ca26'
CORS(app)

# Ensure ML path is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..'))

from ml.predict import make_prediction, get_shap_explanation

# ==========================================
# IPFS & BLOCKCHAIN CONFIG
# ==========================================

IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"
IPFS_CAT_URL = "http://127.0.0.1:5001/api/v0/cat"
IPFS_STORAGE_DIR = os.path.join(BASE_DIR, "ipfs_storage")
os.makedirs(IPFS_STORAGE_DIR, exist_ok=True)

def store_in_ipfs(file_bytes):
    try:
        files = {'file': file_bytes}
        response = requests.post(IPFS_API_URL, files=files, timeout=3)
        if response.status_code == 200:
            return response.json()['Hash']
    except Exception:
        pass
    
    ipfs_hash = "Qm" + hashlib.sha256(file_bytes).hexdigest()[:44]
    file_path = os.path.join(IPFS_STORAGE_DIR, ipfs_hash)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return ipfs_hash

def cat_from_ipfs(ipfs_hash):
    try:
        cat_res = requests.post(f"{IPFS_CAT_URL}?arg={ipfs_hash}", timeout=3)
        if cat_res.status_code == 200:
            return cat_res.content
    except Exception:
        pass

    file_path = os.path.join(IPFS_STORAGE_DIR, ipfs_hash)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()
    raise FileNotFoundError(f"IPFS Hash {ipfs_hash} not found locally or on IPFS daemon")

# ==========================================
# AUTH MIDDLEWARE
# ==========================================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Authorization Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data
        except Exception as e:
            return jsonify({'message': 'Token is invalid or expired!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# ==========================================
# AUTH ROUTES
# ==========================================

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'message': 'Request body must be JSON!'}), 400

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'message': 'Missing fields!'}), 400

    if role not in ('patient', 'doctor', 'admin'):
        return jsonify({'message': 'Role must be patient, doctor, or admin!'}), 400

    # Secure password hashing (PBKDF2 SHA256)
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    conn = db.get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
            (username, hashed_password, role)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'User already exists!'}), 409
    finally:
        conn.close()

    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Request body must be JSON!'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing credentials!'}), 400

    conn = db.get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid Username or Password!'}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        'token': token,
        'role': user['role'],
        'username': user['username']
    })

# ==========================================
# PROTECTED ROUTES
# ==========================================

@app.route('/upload_record', methods=['POST'])
@token_required
def upload_record(current_user):
    """Fallback manual upload route: Patient uploads raw files directly to IPFS and ledger."""
    if current_user.get('role') not in ['patient', 'doctor']:
        return jsonify({'message': 'Unauthorized role'}), 403

    file = request.files.get('file')
    patient_id = request.form.get('patient_id')

    if not file or not patient_id:
        return jsonify({'message': 'Missing file or patient_id'}), 400

    # Upload to IPFS
    try:
        file_bytes = file.read()
        ipfs_hash = store_in_ipfs(file_bytes)
    except Exception as e:
        return jsonify({'message': f'IPFS Error: {str(e)}'}), 500

    # Blockchain entry
    record_id = f"ehr_{os.urandom(4).hex()}"
    
    # Store standard manual upload payload in MLPrediction field
    manual_metadata = {
        "prediction": request.form.get('prediction', 'Not Evaluated'),
        "risk_score": 0.0,
        "risk_level": "N/A",
        "timestamp": datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "doctor_id": current_user.get('username') if current_user.get('role') == 'doctor' else "N/A",
        "doctor_notes": "Manually uploaded document",
        "type": "manual"
    }
    
    fabric_response = fabric_utils.create_ehr_record(
        record_id=record_id,
        patient_id=patient_id,
        ipfs_hash=ipfs_hash,
        prediction=json.dumps(manual_metadata)
    )

    if fabric_response.get("status") == "Failed":
        return jsonify({"error": "Failed to create record on blockchain", "details": fabric_response.get("error")}), 500

    return jsonify({
        "record_id": record_id,
        "patient": patient_id,
        "ipfs_hash": ipfs_hash,
        "prediction": manual_metadata["prediction"],
        "fabric_response": fabric_response
    })


@app.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    """Run prediction on input vitals (17 features) without saving to the ledger."""
    if not request.json:
        return jsonify({"error": "Request body must be JSON"}), 400

    vitals = request.json.get('vitals')
    if not vitals:
        return jsonify({"error": "Missing vitals dictionary"}), 400

    try:
        prediction_res = make_prediction(vitals)
        try:
            shap_image = get_shap_explanation(vitals)
            prediction_res["shap_image"] = shap_image
        except Exception as e:
            prediction_res["shap_error"] = str(e)
            
        from ml.recommendations import get_recommendations
        prediction_res["recommendations"] = get_recommendations(prediction_res["prediction"])
        return jsonify(prediction_res), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/extract_vitals', methods=['POST'])
@token_required
def extract_vitals(current_user):
    """Fetch PDF from IPFS and extract vitals using NLP/Regex."""
    if current_user.get('role') != 'doctor':
        return jsonify({'error': 'Unauthorized. Only doctors can extract vitals.'}), 403

    data = request.json
    ipfs_hash = data.get('ipfs_hash')
    if not ipfs_hash:
        return jsonify({"error": "Missing ipfs_hash"}), 400

    try:
        pdf_bytes = cat_from_ipfs(ipfs_hash)

        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        vitals = {}
        patterns = {
            "Age": r"(?i)age[\s:]+(\d+)",
            "Gender": r"(?i)gender[\s:]+(male|female|m|f)",
            "Glucose": r"(?i)glucose[\s:]+(\d+\.?\d*)",
            "Blood Pressure": r"(?i)blood pressure[\s:]+(\d+\.?\d*)",
            "BMI": r"(?i)bmi[\s:]+(\d+\.?\d*)",
            "Oxygen Saturation": r"(?i)oxygen\s*(?:saturation|sat|level)?[\s:]+(\d+\.?\d*)",
            "Cholesterol": r"(?i)cholesterol[\s:]+(\d+\.?\d*)",
            "Triglycerides": r"(?i)triglycerides[\s:]+(\d+\.?\d*)",
            "HbA1c": r"(?i)hba1c[\s:]+(\d+\.?\d*)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                val = match.group(1).strip()
                if key != "Gender":
                    try:
                        vitals[key] = float(val) if '.' in val else int(val)
                    except ValueError:
                        pass
                else:
                    if val.lower() in ["m", "male"]:
                        vitals[key] = "Male"
                    elif val.lower() in ["f", "female"]:
                        vitals[key] = "Female"

        return jsonify({"vitals": vitals}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/create_prediction_record', methods=['POST'])
@token_required
def create_prediction_record(current_user):
    """
    Run prediction, compile PDF report, upload to IPFS, and anchor metadata to Hyperledger Fabric.
    Restricted to Doctors.
    """
    if current_user.get('role') != 'doctor':
        return jsonify({'message': 'Unauthorized. Only doctors can perform this operation.'}), 403

    data = request.json
    if not data:
        return jsonify({'message': 'Request body must be JSON!'}), 400

    patient_id = data.get('patient_id')
    vitals = data.get('vitals')
    doctor_notes = data.get('doctor_notes', '')
    target_ehr_id = data.get('target_ehr_id', '').strip()

    if not patient_id or not vitals:
        return jsonify({'message': 'Missing patient_id or vitals!'}), 400

    try:
        # 1. Run disease prediction
        prediction_res = make_prediction(vitals)
        
        # 2. Generate Clinical PDF report
        pdf_filename = f"report_{patient_id}_{os.urandom(4).hex()}.pdf"
        pdf_dir = os.path.join(BASE_DIR, "reports")
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        from report_generator import generate_patient_pdf
        generate_patient_pdf(
            patient_id=patient_id,
            doctor_id=current_user.get('username'),
            prediction_data=prediction_res,
            patient_vitals=vitals,
            doctor_notes=doctor_notes,
            output_path=pdf_path
        )
        
        # 3. Upload report to IPFS
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            ipfs_hash = store_in_ipfs(pdf_bytes)
        except Exception as e:
            return jsonify({'message': f'IPFS Error during PDF upload: {str(e)}'}), 500
            
        # 4. Inscribe ONLY patient ID, prediction details, risk score, report CID, timestamp, doctor ID
        prediction_metadata = {
            "prediction": prediction_res["prediction"],
            "risk_score": float(prediction_res["confidence_score"]),
            "risk_level": prediction_res["risk_level"],
            "timestamp": datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "doctor_id": current_user.get('username'),
            "doctor_notes": doctor_notes,
            "type": "prediction",
            "imputed_count": prediction_res.get("imputed_count", 0),
            "extracted_count": prediction_res.get("extracted_count", 0)
        }
        
        # Use target_ehr_id if provided (evaluating existing record), otherwise generate a new one
        record_id = target_ehr_id if target_ehr_id else f"ehr_{os.urandom(4).hex()}"
        fabric_response = fabric_utils.create_ehr_record(
            record_id=record_id,
            patient_id=patient_id,
            ipfs_hash=ipfs_hash,
            prediction=json.dumps(prediction_metadata)
        )
        
        if fabric_response.get("status") == "Failed":
            return jsonify({"error": "Failed to write record to Hyperledger Fabric", "details": fabric_response.get("error")}), 500
            
        # 5. Automatically authorize the creating doctor to view the record
        fabric_utils.grant_access(record_id, current_user.get('username'))
        
        return jsonify({
            "record_id": record_id,
            "patient_id": patient_id,
            "ipfs_hash": ipfs_hash,
            "prediction": prediction_res["prediction"],
            "confidence_score": prediction_res["confidence_score"],
            "risk_level": prediction_res["risk_level"],
            "fabric_response": fabric_response
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download_report/<record_id>', methods=['GET'])
@token_required
def download_report(current_user, record_id):
    """Retrieve the clinical report PDF directly from IPFS after verifying blockchain authorizations."""
    username = current_user.get('username')
    
    # 1. Fetch all records from ledger to verify authorization
    response = fabric_utils.query_chaincode("GetAllRecords", [])
    if response.get('status') != 'Success':
        return jsonify({"error": "Failed to query ledger", "details": response.get('error')}), 500
        
    records = response.get('data', [])
    target_record = None
    
    for r in records:
        if r.get('id') == record_id:
            target_record = r
            break
            
    if not target_record:
        return jsonify({"error": "EHR record not found"}), 404
        
    # Verify RBAC access
    is_authorized = (target_record.get('patientId') == username or 
                     username in target_record.get('authorizedUsers', []))
                     
    if not is_authorized and current_user.get('role') != 'admin':
        return jsonify({"error": "Unauthorized access to this patient record"}), 403
        
    # 2. Stream PDF directly from IPFS daemon cat api or local fallback
    ipfs_hash = target_record.get('ipfsHash')
    try:
        pdf_bytes = cat_from_ipfs(ipfs_hash)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-disposition": f"attachment; filename=clinical_report_{record_id}.pdf"}
        )
    except Exception as e:
        return jsonify({"error": f"Failed to download from IPFS: {str(e)}"}), 500


@app.route('/grant_access', methods=['POST'])
@token_required
def grant_access(current_user):
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    record_id = data.get('record_id')
    doctor_id = data.get('doctor_id')

    if not record_id or not doctor_id:
        return jsonify({"error": "Missing record_id or doctor_id"}), 400

    record_id = record_id.strip()
    doctor_id = doctor_id.strip()

    fabric_response = fabric_utils.grant_access(record_id, doctor_id)
    
    if fabric_response.get("status") == "Failed":
        return jsonify({"error": "Failed to grant access", "details": fabric_response.get("error")}), 500

    return jsonify({
        "status": "Success",
        "fabric_response": fabric_response
    })


@app.route('/get_my_records', methods=['GET'])
@token_required
def get_my_records(current_user):
    """Retrieve blockchain records belonging to the patient."""
    username = current_user.get('username')
    response = fabric_utils.query_chaincode("GetAllRecords", [])
    
    if response.get('status') == 'Success':
        all_records = response.get('data', []) or []
        if isinstance(all_records, list):
            my_records = [r for r in all_records if r.get('patientId') == username]
        else:
            my_records = []
        return jsonify(my_records), 200
    else:
        return jsonify({"error": response.get('error')}), 500


@app.route('/get_records_by_doctor', methods=['GET'])
@token_required
def get_records_by_doctor(current_user):
    """Retrieve blockchain records shared with the calling doctor."""
    if current_user.get('role') != 'doctor':
        return jsonify({"error": "Unauthorized role. Doctors only."}), 403

    doctor_username = current_user.get('username')
    response = fabric_utils.get_records_by_doctor(doctor_username)

    if response.get('status') == 'Success':
        data = response.get('data') or []
        return jsonify(data), 200
    else:
        return jsonify({"error": response.get('error')}), 500


@app.route('/get_records', methods=['GET'])
@token_required
def get_records(current_user):
    """Retrieve all blockchain records (accessible by admin)."""
    response = fabric_utils.query_chaincode("GetAllRecords", [])

    if response.get('status') == 'Success':
        data = response.get('data') or []
        return jsonify(data), 200
    else:
        return jsonify({"error": response.get('error')}), 500

# ==========================================
# ADMIN DASHBOARD ENDPOINTS
# ==========================================

@app.route('/admin/users', methods=['GET'])
@token_required
def admin_users(current_user):
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Admin access only!'}), 403
    conn = db.get_db_connection()
    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users]), 200


@app.route('/admin/stats', methods=['GET'])
@token_required
def admin_stats(current_user):
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Admin access only!'}), 403
        
    conn = db.get_db_connection()
    patient_count = conn.execute("SELECT count(*) FROM users WHERE role='patient'").fetchone()[0]
    doctor_count = conn.execute("SELECT count(*) FROM users WHERE role='doctor'").fetchone()[0]
    conn.close()
    
    total_records = 0
    response = fabric_utils.query_chaincode("GetAllRecords", [])
    if response.get('status') == 'Success':
        records = response.get('data', [])
        if isinstance(records, list):
            total_records = len(records)
            
    return jsonify({
        "patients": patient_count,
        "doctors": doctor_count,
        "records": total_records
    }), 200


@app.route('/admin/docker_status', methods=['GET'])
@token_required
def admin_docker_status(current_user):
    import subprocess
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Admin access only!'}), 403
        
    try:
        res = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"],
            capture_output=True,
            text=True,
            check=True
        )
        containers = []
        for line in res.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 3:
                    containers.append({
                        "name": parts[0],
                        "status": parts[1],
                        "image": parts[2]
                    })
        return jsonify({"status": "success", "containers": containers}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# HEALTH CHECK
# ==========================================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "ehr-backend"}), 200

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)