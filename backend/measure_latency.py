import time
import numpy as np
import uuid
import json
import subprocess
import sys
import os

# Ensure backend folder is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fabric_utils as fu

def run_benchmark():
    print("Starting 30-trial replication/revocation latency benchmark...")
    print("Measuring full transaction life-cycle (endorsement on Org1/Org2 -> ordering -> commitment on Org2 ledger)...")
    
    latencies = []
    
    # We will use CreateRecord to simulate writing a token revocation state to the ledger
    for trial in range(30):
        # Unique record representing a revoked token
        record_id = f"revoc_tok_{trial}_{uuid.uuid4().hex[:4]}"
        patient_id = "patient_revoc"
        ipfs_hash = "QmRevokedToken"
        revocation_data = "STATUS_REVOKED"
        
        # Start high-precision timer
        t0 = time.perf_counter()
        
        # Submit transaction on Org1 (runs peer chaincode invoke targeting Org1/Org2 with --waitForEvent)
        res = fu.create_ehr_record(record_id, patient_id, ipfs_hash, revocation_data)
        
        # Stop timer
        t1 = time.perf_counter()
        
        if res.get("status") == "Success":
            latency = (t1 - t0) * 1000  # convert to milliseconds
            latencies.append(latency)
            print(f"Trial {trial+1}/30: {latency:.2f} ms")
        else:
            print(f"Trial {trial+1}/30: FAILED - {res.get('error')}")
            
    if latencies:
        mean_lat = np.mean(latencies)
        std_lat = np.std(latencies)
        print("\n=== REVOCATION LATENCY BENCHMARK RESULTS ===")
        print(f"Number of trials: {len(latencies)}")
        print(f"Mean Latency: {mean_lat:.2f} ms")
        print(f"Standard Deviation: {std_lat:.2f} ms")
        print(f"Min Latency: {np.min(latencies):.2f} ms")
        print(f"Max Latency: {np.max(latencies):.2f} ms")
    else:
        print("No successful trials completed.")

if __name__ == "__main__":
    run_benchmark()
