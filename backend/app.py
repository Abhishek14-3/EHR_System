from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import requests
import os
import fabric_utils
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from datetime import timezone
from functools import wraps
import db
import sqlite3

# ==========================================
# INITIAL SETUP
# ==========================================

# Initialize Database
db.init_db()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c5c645e5b3ee0b89f8121fc09440bf5e22ea1f681a96ca26'
CORS(app)

# ==========================================
# LOAD ML MODELS (FIXED PATH ISSUE ✅)
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, '..', 'ml_model', 'heart_model.joblib')
scaler_path = os.path.join(BASE_DIR, '..', 'ml_model', 'scaler.joblib')

print("Loading model from:", model_path)
print("Loading scaler from:", scaler_path)

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

if not os.path.exists(scaler_path):
    raise FileNotFoundError(f"Scaler file not found at {scaler_path}")

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# ==========================================
# IPFS CONFIG
# ==========================================

IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"

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

    if role not in ('patient', 'doctor'):
        return jsonify({'message': 'Role must be patient or doctor!'}), 400

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

    if current_user.get('role') not in ['patient', 'doctor']:
        return jsonify({'message': 'Unauthorized role'}), 403

    file = request.files.get('file')
    patient_id = request.form.get('patient_id')

    if not file or not patient_id:
        return jsonify({'message': 'Missing file or patient_id'}), 400

    # Upload to IPFS
    try:
        files = {'file': file.read()}
        response = requests.post(IPFS_API_URL, files=files)
        response.raise_for_status()
        ipfs_hash = response.json()['Hash']
    except requests.exceptions.ConnectionError:
        return jsonify({
            'message': 'Failed to connect to IPFS node. Please ensure it is running on port 5001.'
        }), 503
    except Exception as e:
        return jsonify({'message': f'IPFS Error: {str(e)}'}), 500

    # Blockchain entry
    record_id = f"ehr_{os.urandom(4).hex()}"
    prediction = request.form.get('prediction', 'Not Evaluated')

    fabric_response = fabric_utils.create_ehr_record(
        record_id=record_id,
        patient_id=patient_id,
        ipfs_hash=ipfs_hash,
        prediction=prediction
    )

    if fabric_response.get("status") == "Failed":
        return jsonify({"error": "Failed to create record on blockchain", "details": fabric_response.get("error")}), 500

    return jsonify({
        "record_id": record_id,
        "patient": patient_id,
        "ipfs_hash": ipfs_hash,
        "prediction": prediction,
        "fabric_response": fabric_response
    })


@app.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    if not request.json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.json.get('features')

    if not data:
        return jsonify({"error": "Missing features"}), 400

    try:
        scaled_data = scaler.transform([data])
        prediction = model.predict(scaled_data)[0]

        return jsonify({
            "prediction": "Heart Disease" if prediction == 1 else "Healthy"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/grant_access', methods=['POST'])
@token_required
def grant_access(current_user):
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    record_id = data.get('record_id')
    doctor_id = data.get('doctor_id')

    print(f"[GRANT ACCESS] record_id='{record_id}', doctor_id='{doctor_id}', user={current_user.get('username')}")

    if not record_id or not doctor_id:
        return jsonify({"error": "Missing record_id or doctor_id"}), 400

    # Strip whitespace to avoid invisible character issues
    record_id = record_id.strip()
    doctor_id = doctor_id.strip()

    fabric_response = fabric_utils.grant_access(record_id, doctor_id)
    
    print(f"[GRANT ACCESS] Fabric response: {fabric_response}")
    
    if fabric_response.get("status") == "Failed":
        return jsonify({"error": "Failed to grant access", "details": fabric_response.get("error")}), 500

    return jsonify({
        "status": "Success",
        "fabric_response": fabric_response
    })


@app.route('/get_my_records', methods=['GET'])
@token_required
def get_my_records(current_user):
    """Get all records belonging to the currently logged-in patient."""
    username = current_user.get('username')
    
    # Query ALL records from blockchain
    response = fabric_utils.query_chaincode("GetAllRecords", [])
    
    if response.get('status') == 'Success':
        all_records = response.get('data', []) or []  # Handle null/None from chaincode
        # Filter records where patientId matches current user
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

    if current_user.get('role') != 'doctor':
        return jsonify({"error": "Doctors only"}), 403

    doctor_username = current_user.get('username')

    response = fabric_utils.get_records_by_doctor(doctor_username)

    if response.get('status') == 'Success':
        data = response.get('data') or []  # Handle null/None from chaincode
        return jsonify(data), 200
    else:
        return jsonify({"error": response.get('error')}), 500


@app.route('/get_records', methods=['GET'])
@token_required
def get_records(current_user):

    response = fabric_utils.query_chaincode("GetAllRecords", [])

    if response.get('status') == 'Success':
        data = response.get('data') or []  # Handle null/None from chaincode
        return jsonify(data), 200
    else:
        return jsonify({"error": response.get('error')}), 500


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint — no auth required."""
    return jsonify({"status": "ok", "service": "ehr-backend"}), 200

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    app.run(port=5000, debug=True)