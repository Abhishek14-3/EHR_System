import subprocess
import json
import uuid
import os
import re

CLI_CONTAINER = "peer0.org1.example.com"
PEER2_CONTAINER = "peer0.org2.example.com"
CHANNEL_NAME = "mychannel"
CHAINCODE_NAME = "ehr"

def ensure_fabric_credentials():
    """
    Since we are explicitly NOT using the `cli` container, we must inject proper identities:
    1. Orderer TLS CA Cert: To communicate securely with the orderer.
    2. User1 MSP for Org1: To satisfy the channel's "Writers Policy". 
       (The default peer certificate at /etc/hyperledger/fabric/msp lacks Writer permissions).
    3. Org2 TLS CA Cert: To allow peer0.org1 to communicate with peer0.org2 for dual endorsement.
    """
    try:
        # 1. ALWAYS Refresh Orderer TLS Cert to prevent stale test-network certificates
        subprocess.run(["docker", "exec", CLI_CONTAINER, "rm", "-f", "/tmp/orderer_ca.crt"], capture_output=True)
        subprocess.run(["docker", "cp", "orderer.example.com:/var/hyperledger/orderer/tls/ca.crt", "orderer_ca.crt"], check=True, capture_output=True)
        subprocess.run(["docker", "cp", "orderer_ca.crt", f"{CLI_CONTAINER}:/tmp/orderer_ca.crt"], check=True, capture_output=True)
        if os.path.exists("orderer_ca.crt"): os.remove("orderer_ca.crt")
            
        # 2. ALWAYS Refresh User1 MSP for Org1 (Canonical Writer Identity)
        subprocess.run(["docker", "exec", CLI_CONTAINER, "rm", "-rf", "/tmp/user_msp"], capture_output=True)
        # We execute this copy operation via WSL since the fabric-samples are generated inside WSL Linux.
        user_msp_wsl = "/home/abhishek/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp"
        subprocess.run(["wsl", "docker", "cp", user_msp_wsl, f"{CLI_CONTAINER}:/tmp/user_msp"], check=True, capture_output=True)
        
        # 3. ALWAYS Refresh Org2 TLS CA Cert (needed for dual-peer endorsement)
        subprocess.run(["docker", "exec", CLI_CONTAINER, "rm", "-f", "/tmp/org2_tls_ca.crt"], capture_output=True)
        subprocess.run(["docker", "cp", f"{PEER2_CONTAINER}:/etc/hyperledger/fabric/tls/ca.crt", "org2_tls_ca.crt"], check=True, capture_output=True)
        subprocess.run(["docker", "cp", "org2_tls_ca.crt", f"{CLI_CONTAINER}:/tmp/org2_tls_ca.crt"], check=True, capture_output=True)
        if os.path.exists("org2_tls_ca.crt"): os.remove("org2_tls_ca.crt")
            
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not provision Fabric identities. Command Failed: {e.stderr}")

def invoke_chaincode(function_name, args):
    # Dynamically inject credentials if missing
    ensure_fabric_credentials()

    args_json = json.dumps({
        "function": function_name,
        "Args": args
    })

    print(f"[FABRIC] Invoking {function_name} with args: {args}")

    # Execute chaincode directly on the peer container!
    # IMPORTANT: Endorsement policy requires BOTH Org1 and Org2 peers
    command = [
        "docker", "exec",
        "-e", "CORE_PEER_LOCALMSPID=Org1MSP",
        "-e", "CORE_PEER_TLS_ENABLED=true",
        
        # KEY CHANGE: Using the User1 MSP identity instead of the peer identity
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
        # Peer 1 (Org1) endorsement
        "--peerAddresses", "peer0.org1.example.com:7051",
        "--tlsRootCertFiles", "/etc/hyperledger/fabric/tls/ca.crt",
        # Peer 2 (Org2) endorsement — matches what the CLI does
        "--peerAddresses", "peer0.org2.example.com:9051",
        "--tlsRootCertFiles", "/tmp/org2_tls_ca.crt",
        "--waitForEvent",
        "-c", args_json
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"[FABRIC] SUCCESS stdout: {result.stdout}")
        print(f"[FABRIC] SUCCESS stderr: {result.stderr}")
        return {
            "status": "Success",
            "txn_id": str(uuid.uuid4())[:8],
            "output": result.stdout
        }

    except subprocess.CalledProcessError as e:
        # Strip ANSI codes for cleaner UI error messages
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_err = ansi_escape.sub('', e.stderr if e.stderr else "")
        
        print(f"[FABRIC] FAILED stdout: {e.stdout}")
        print(f"[FABRIC] FAILED stderr: {clean_err}")
        
        # Try to extract the specific chaincode error message
        match = re.search(r'message:"([^"]+)"', clean_err)
        friendly_err = match.group(1) if match else clean_err.strip().split('\n')[-1]
        
        print("ERROR:", friendly_err)
        return {
            "status": "Failed",
            "error": friendly_err
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
        
        # Parse output safely as JSON resolving the standard Fabric chaincode query response 
        try:
            # If the chaincode returned an empty result, Fabric may just return empty string instead of []
            if not result.stdout.strip():
                return {"status": "Success", "data": []}
            parsed_data = json.loads(result.stdout)
            # Go's json.Marshal produces `null` for nil slices; normalize to []
            if parsed_data is None:
                parsed_data = []
            return {"status": "Success", "data": parsed_data}
        except json.JSONDecodeError:
            return {"status": "Success", "data": result.stdout.strip()}

    except subprocess.CalledProcessError as e:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_err = ansi_escape.sub('', e.stderr if e.stderr else "")
        
        match = re.search(r'message:"([^"]+)"', clean_err)
        friendly_err = match.group(1) if match else clean_err.strip().split('\n')[-1]
        
        print("ERROR:", friendly_err)
        return {
            "status": "Failed",
            "error": friendly_err
        }

def get_records_by_doctor(doctor_id):
    return query_chaincode("GetRecordsByDoctor", [str(doctor_id)])