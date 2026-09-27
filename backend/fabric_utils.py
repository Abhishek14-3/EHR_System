import subprocess
import json
import uuid
import os
import re
import db

CLI_CONTAINER = "peer0.org1.example.com"
PEER2_CONTAINER = "peer0.org2.example.com"
CHANNEL_NAME = "mychannel"
CHAINCODE_NAME = "ehr"

def _is_docker_available():
    try:
        res = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False

# ==========================================
# LOCAL FALLBACK LEDGER HELPERS
# ==========================================

def _db_create_record(record_id, patient_id, ipfs_hash, prediction):
    conn = db.get_db_connection()
    try:
        conn.execute(
            'INSERT OR REPLACE INTO mock_records (id, patient_id, ipfs_hash, prediction, authorized_users) VALUES (?, ?, ?, ?, ?)',
            (record_id, patient_id, ipfs_hash, prediction, json.dumps([patient_id]))
        )
        conn.commit()
        return {"status": "Success", "txn_id": str(uuid.uuid4())[:8], "mode": "local_fallback"}
    finally:
        conn.close()

def _db_grant_access(record_id, doctor_id):
    conn = db.get_db_connection()
    try:
        row = conn.execute('SELECT * FROM mock_records WHERE id = ?', (record_id,)).fetchone()
        if not row:
            return {"status": "Failed", "error": f"Record {record_id} not found"}
        auth_users = json.loads(row['authorized_users'])
        if doctor_id not in auth_users:
            auth_users.append(doctor_id)
        conn.execute('UPDATE mock_records SET authorized_users = ? WHERE id = ?', (json.dumps(auth_users), record_id))
        conn.commit()
        return {"status": "Success", "txn_id": str(uuid.uuid4())[:8], "mode": "local_fallback"}
    finally:
        conn.close()

def _db_get_all_records():
    conn = db.get_db_connection()
    try:
        rows = conn.execute('SELECT * FROM mock_records').fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r['id'],
                "patientId": r['patient_id'],
                "ipfsHash": r['ipfs_hash'],
                "prediction": r['prediction'],
                "authorizedUsers": json.loads(r['authorized_users'])
            })
        return {"status": "Success", "data": result}
    finally:
        conn.close()

def _db_get_records_by_doctor(doctor_id):
    conn = db.get_db_connection()
    try:
        rows = conn.execute('SELECT * FROM mock_records').fetchall()
        result = []
        for r in rows:
            auth_users = json.loads(r['authorized_users'])
            if doctor_id in auth_users:
                result.append({
                    "id": r['id'],
                    "patientId": r['patient_id'],
                    "ipfsHash": r['ipfs_hash'],
                    "prediction": r['prediction'],
                    "authorizedUsers": auth_users
                })
        return {"status": "Success", "data": result}
    finally:
        conn.close()


def ensure_fabric_credentials():
    """
    Ensure required MSP and TLS certificates exist inside the CLI container.
    Uses unique temp files and safe cleanup to prevent Windows [WinError 32] file locking conflicts.
    """
    if not _is_docker_available():
        return
    try:
        # Check if certs are already provisioned inside CLI container
        check_cmd = ["docker", "exec", CLI_CONTAINER, "sh", "-c", "test -f /tmp/orderer_ca.crt && test -d /tmp/user_msp && test -f /tmp/org2_tls_ca.crt"]
        res = subprocess.run(check_cmd, capture_output=True)
        if res.returncode == 0:
            return  # Credentials already in place inside container!

        # 1. Orderer TLS CA Cert
        subprocess.run(["docker", "exec", CLI_CONTAINER, "rm", "-f", "/tmp/orderer_ca.crt"], capture_output=True)
        tmp_orderer = f"orderer_ca_{uuid.uuid4().hex[:6]}.crt"
        try:
            subprocess.run(["docker", "cp", "orderer.example.com:/var/hyperledger/orderer/tls/ca.crt", tmp_orderer], check=True, capture_output=True)
            subprocess.run(["docker", "cp", tmp_orderer, f"{CLI_CONTAINER}:/tmp/orderer_ca.crt"], check=True, capture_output=True)
        finally:
            if os.path.exists(tmp_orderer):
                try:
                    os.remove(tmp_orderer)
                except OSError:
                    pass

        # 2. User1 MSP for Org1 (Canonical Writer Identity)
        subprocess.run(["docker", "exec", CLI_CONTAINER, "rm", "-rf", "/tmp/user_msp"], capture_output=True)
        user_msp_wsl = "/home/abhishek/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp"
        subprocess.run(["wsl", "docker", "cp", user_msp_wsl, f"{CLI_CONTAINER}:/tmp/user_msp"], check=True, capture_output=True)

        # 3. Org2 TLS CA Cert (needed for dual-peer endorsement)
        subprocess.run(["docker", "exec", CLI_CONTAINER, "rm", "-f", "/tmp/org2_tls_ca.crt"], capture_output=True)
        tmp_org2 = f"org2_tls_ca_{uuid.uuid4().hex[:6]}.crt"
        try:
            subprocess.run(["docker", "cp", f"{PEER2_CONTAINER}:/etc/hyperledger/fabric/tls/ca.crt", tmp_org2], check=True, capture_output=True)
            subprocess.run(["docker", "cp", tmp_org2, f"{CLI_CONTAINER}:/tmp/org2_tls_ca.crt"], check=True, capture_output=True)
        finally:
            if os.path.exists(tmp_org2):
                try:
                    os.remove(tmp_org2)
                except OSError:
                    pass

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not provision Fabric identities. Command Failed: {e.stderr}")

def invoke_chaincode(function_name, args):
    if not _is_docker_available():
        if function_name == "CreateRecord":
            return _db_create_record(args[0], args[1], args[2], args[3])
        elif function_name == "GrantAccess":
            return _db_grant_access(args[0], args[1])

    # Dynamically inject credentials if missing
    ensure_fabric_credentials()

    args_json = json.dumps({
        "function": function_name,
        "Args": args
    })

    print(f"[FABRIC] Invoking {function_name} with args: {args}")

    command = [
        "docker", "exec",
        "-e", "CORE_PEER_LOCALMSPID=Org1MSP",
        "-e", "CORE_PEER_TLS_ENABLED=true",
        "-e", "CORE_PEER_MSPCONFIGPATH=/tmp/user_msp", 
        "-e", "CORE_PEER_ADDRESS=peer0.org1.example.com:7051",
        "-e", "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
        
        CLI_CONTAINER,

        "peer", "chaincode", "invoke",
        "-o", "orderer.example.com:7050",
        "--ordererTLSHostnameOverride", "orderer.example.com",
        "--tls",
        "--cafile", "/tmp/orderer_ca.crt",
        "-C", CHANNEL_NAME,
        "-n", CHAINCODE_NAME,
        "--peerAddresses", "peer0.org1.example.com:7051",
        "--tlsRootCertFiles", "/etc/hyperledger/fabric/tls/ca.crt",
        "--peerAddresses", "peer0.org2.example.com:9051",
        "--tlsRootCertFiles", "/tmp/org2_tls_ca.crt",
        "--waitForEvent",
        "-c", args_json
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"[FABRIC] SUCCESS stdout: {result.stdout}")
        return {
            "status": "Success",
            "txn_id": str(uuid.uuid4())[:8],
            "output": result.stdout
        }

    except Exception as e:
        # Fall back to local DB if Docker fails
        if function_name == "CreateRecord":
            return _db_create_record(args[0], args[1], args[2], args[3])
        elif function_name == "GrantAccess":
            return _db_grant_access(args[0], args[1])

        return {
            "status": "Failed",
            "error": str(e)
        }

def create_ehr_record(record_id, patient_id, ipfs_hash, prediction):
    return invoke_chaincode(
        "CreateRecord",
        [str(record_id), str(patient_id), str(ipfs_hash), str(prediction)]
    )

def grant_access(record_id, doctor_id):
    return invoke_chaincode(
        "GrantAccess",
        [str(record_id), str(doctor_id)]
    )

def query_chaincode(function_name, args):
    if not _is_docker_available():
        if function_name == "GetAllRecords":
            return _db_get_all_records()
        elif function_name == "GetRecordsByDoctor":
            return _db_get_records_by_doctor(args[0] if args else "")

    ensure_fabric_credentials()

    args_json = json.dumps({
        "function": function_name,
        "Args": args
    })

    command = [
        "docker", "exec",
        "-e", "CORE_PEER_LOCALMSPID=Org1MSP",
        "-e", "CORE_PEER_TLS_ENABLED=true",
        "-e", "CORE_PEER_MSPCONFIGPATH=/tmp/user_msp", 
        "-e", "CORE_PEER_ADDRESS=peer0.org1.example.com:7051",
        "-e", "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
        
        CLI_CONTAINER,

        "peer", "chaincode", "query",
        "-C", CHANNEL_NAME,
        "-n", CHAINCODE_NAME,
        "-c", args_json
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        try:
            if not result.stdout.strip():
                return {"status": "Success", "data": []}
            parsed_data = json.loads(result.stdout)
            if parsed_data is None:
                parsed_data = []
            return {"status": "Success", "data": parsed_data}
        except json.JSONDecodeError:
            return {"status": "Success", "data": result.stdout.strip()}

    except Exception:
        if function_name == "GetAllRecords":
            return _db_get_all_records()
        elif function_name == "GetRecordsByDoctor":
            return _db_get_records_by_doctor(args[0] if args else "")
        return {
            "status": "Failed",
            "error": "Could not query chaincode"
        }

def get_records_by_doctor(doctor_id):
    return query_chaincode("GetRecordsByDoctor", [str(doctor_id)])