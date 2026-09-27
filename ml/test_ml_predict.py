import sys
import os
import json

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.predict import make_prediction, get_shap_explanation

def run_tests():
    print("==========================================")
    print(" HEALTHCHAIN ML MODULE VERIFICATION TEST ")
    print("==========================================")

    # Test Case A: Fully Normal Patient
    print("\n--- TEST CASE (A): Fully Normal Patient ---")
    patient_a = {
        "Age": 32, "Gender": "Female", "Glucose": 88.0, "Blood Pressure": 112.0,
        "BMI": 21.5, "Oxygen Saturation": 98.5, "LengthOfStay": 2, "Cholesterol": 175.0,
        "Triglycerides": 120.0, "HbA1c": 5.1, "Smoking": 0, "Alcohol": 0,
        "Physical Activity": 6.0, "Diet Score": 8.0, "Family History": 0,
        "Stress Level": 3.0, "Sleep Hours": 7.5
    }
    res_a = make_prediction(patient_a)
    print(json.dumps(res_a, indent=2))

    # Test Case B: Patient with missing fields (>5 missing fields)
    print("\n--- TEST CASE (B): Patient with Excessive Missing Fields ---")
    patient_b = {
        "Age": 45, "Gender": "Male"
        # 15 fields missing!
    }
    try:
        res_b = make_prediction(patient_b)
        print(json.dumps(res_b, indent=2))
    except Exception as e:
        print(f"EXPECTED REJECTION ERROR: {e}")

    # Test Case C: Clearly Diseased Patient (Diabetes/High Glucose/HbA1c)
    print("\n--- TEST CASE (C): Clearly Diseased Patient (Severe Diabetic Profile) ---")
    patient_c = {
        "Age": 62, "Gender": "Male", "Glucose": 245.0, "Blood Pressure": 155.0,
        "BMI": 34.2, "Oxygen Saturation": 95.0, "LengthOfStay": 6, "Cholesterol": 260.0,
        "Triglycerides": 280.0, "HbA1c": 10.5, "Smoking": 1, "Alcohol": 1,
        "Physical Activity": 1.0, "Diet Score": 2.0, "Family History": 1,
        "Stress Level": 8.0, "Sleep Hours": 5.0
    }
    res_c = make_prediction(patient_c)
    print(json.dumps(res_c, indent=2))

    # Test Case D: Borderline Patient near "Healthy" thresholds
    print("\n--- TEST CASE (D): Borderline Patient (BP=121 mmHg, just over healthy limit) ---")
    patient_d = {
        "Age": 40, "Gender": "Female", "Glucose": 99.0, "Blood Pressure": 121.0, # BP >= 120 triggers non-healthy check
        "BMI": 24.8, "Oxygen Saturation": 97.0, "LengthOfStay": 3, "Cholesterol": 195.0,
        "Triglycerides": 140.0, "HbA1c": 5.5, "Smoking": 0, "Alcohol": 0,
        "Physical Activity": 4.0, "Diet Score": 6.0, "Family History": 0,
        "Stress Level": 4.0, "Sleep Hours": 7.0
    }
    res_d = make_prediction(patient_d)
    print(json.dumps(res_d, indent=2))

    # Test SHAP Waterfall Plot generation
    print("\n--- TEST SHAP TREEEXPLAINER ---")
    try:
        b64_shap = get_shap_explanation(patient_c)
        print(f"SHAP b64 image string successfully generated (length: {len(b64_shap)} chars)")
    except Exception as e:
        print(f"SHAP Generation Error: {e}")

if __name__ == "__main__":
    run_tests()
