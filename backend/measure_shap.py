import time
import numpy as np
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.predict import make_prediction, get_shap_explanation, load_resources

def run_shap_benchmark():
    print("Initializing ML resources...")
    load_resources()
    
    vitals = {
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
    
    print("Starting 100-trial backend latency benchmark...")
    
    latencies_inf = []
    latencies_shap = []
    
    # Warmup runs (to eliminate first-run plotting/loading overhead)
    print("Running warmup trials...")
    for _ in range(5):
        _ = make_prediction(vitals)
        _ = get_shap_explanation(vitals)
        
    print("Executing 100 timed trials...")
    for trial in range(100):
        # 1. Inference-only component
        t0 = time.perf_counter()
        pred = make_prediction(vitals)
        t1 = time.perf_counter()
        dur_inf = (t1 - t0) * 1000  # ms
        latencies_inf.append(dur_inf)
        
        # 2. SHAP + Inference component (includes matplotlib plot generation)
        t0 = time.perf_counter()
        pred = make_prediction(vitals)
        shap_plot = get_shap_explanation(vitals)
        t1 = time.perf_counter()
        dur_shap = (t1 - t0) * 1000  # ms
        latencies_shap.append(dur_shap)
        
    # Stats
    mean_inf = np.mean(latencies_inf)
    std_inf = np.std(latencies_inf)
    mean_shap = np.mean(latencies_shap)
    std_shap = np.std(latencies_shap)
    
    print("\n==============================================================")
    print("            ML & EXPLAINABILITY LATENCY RESULTS")
    print("==============================================================")
    print(f"Trials: 100")
    print(f"--------------------------------------------------------------")
    print(f"Component                    | Mean Latency | Std Dev   | Min/Max")
    print(f"--------------------------------------------------------------")
    print(f"Inference-Only               | {mean_inf:8.2f} ms | {std_inf:7.2f} ms | {np.min(latencies_inf):.2f}/{np.max(latencies_inf):.2f} ms")
    print(f"SHAP Explainer + Inference   | {mean_shap:8.2f} ms | {std_shap:7.2f} ms | {np.min(latencies_shap):.2f}/{np.max(latencies_shap):.2f} ms")
    print("==============================================================")

if __name__ == "__main__":
    run_shap_benchmark()
