import os
import joblib
import pandas as pd
import numpy as np
import io
import base64
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap

# Resolve path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

best_model_path = os.path.join(MODELS_DIR, "best_model.pkl")
scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
gender_encoder_path = os.path.join(MODELS_DIR, "gender_encoder.pkl")
label_encoder_path = os.path.join(MODELS_DIR, "label_encoder.pkl")
feature_medians_path = os.path.join(MODELS_DIR, "feature_medians.pkl")

# Resources loaded lazily
model = None
scaler = None
gender_encoder = None
label_encoder = None
feature_medians = None
logger = None

def _setup_logger():
    """Setup secure rotating logger without writing raw PHI data."""
    global logger
    if logger is None:
        logger = logging.getLogger("HealthChainML")
        logger.setLevel(logging.INFO)
        log_file = os.path.join(BASE_DIR, "ml_predictions.log")
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def load_resources():
    """Load model resources once into memory."""
    global model, scaler, gender_encoder, label_encoder, feature_medians
    _setup_logger()
    if model is None:
        if not os.path.exists(best_model_path):
            raise FileNotFoundError(f"Model file not found at {best_model_path}")
        model = joblib.load(best_model_path)
    if scaler is None:
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
        scaler = joblib.load(scaler_path)
    if gender_encoder is None:
        if not os.path.exists(gender_encoder_path):
            raise FileNotFoundError(f"Gender encoder file not found at {gender_encoder_path}")
        gender_encoder = joblib.load(gender_encoder_path)
    if label_encoder is None:
        if not os.path.exists(label_encoder_path):
            raise FileNotFoundError(f"Label encoder file not found at {label_encoder_path}")
        label_encoder = joblib.load(label_encoder_path)
    if feature_medians is None:
        if os.path.exists(feature_medians_path):
            feature_medians = joblib.load(feature_medians_path)
        else:
            # Default physiological raw medians from dataset
            feature_medians = {
                'Age': 55.0, 'Glucose': 110.5, 'Blood Pressure': 138.3, 'BMI': 28.05,
                'Oxygen Saturation': 95.3, 'LengthOfStay': 4.0, 'Cholesterol': 211.8,
                'Triglycerides': 173.4, 'HbA1c': 5.97, 'Smoking': 0.0, 'Alcohol': 0.0,
                'Physical Activity': 3.59, 'Diet Score': 3.79, 'Family History': 0.0,
                'Stress Level': 5.9, 'Sleep Hours': 6.23, 'Gender': 'Female'
            }

FEATURE_ORDER = [
    'Age', 'Gender', 'Glucose', 'Blood Pressure', 'BMI', 'Oxygen Saturation', 
    'LengthOfStay', 'Cholesterol', 'Triglycerides', 'HbA1c', 'Smoking', 'Alcohol', 
    'Physical Activity', 'Diet Score', 'Family History', 'Stress Level', 'Sleep Hours'
]

VALID_RANGES = {
    'Age': (0.0, 120.0),
    'Oxygen Saturation': (0.0, 100.0),
    'Blood Pressure': (30.0, 300.0),
    'BMI': (10.0, 100.0),
    'Glucose': (20.0, 1000.0),
    'HbA1c': (2.0, 20.0),
    'Cholesterol': (50.0, 1000.0),
    'Triglycerides': (20.0, 2000.0),
    'Sleep Hours': (0.0, 24.0),
    'LengthOfStay': (0.0, 365.0)
}

CORE_VITALS = [
    'Age', 'Gender', 'Glucose', 'Blood Pressure', 'BMI', 
    'Oxygen Saturation', 'Cholesterol', 'Triglycerides', 'HbA1c'
]

LIFESTYLE_VITALS = [
    'LengthOfStay', 'Smoking', 'Alcohol', 'Physical Activity', 
    'Diet Score', 'Family History', 'Stress Level', 'Sleep Hours'
]

def _validate_and_impute(patient_data):
    """
    Validate input range & missing counts, and impute missing fields using training set medians.
    Never let missing BMI or SpO2 become literal 0.0.
    """
    load_resources()
    missing_count = 0
    imputed_features = []
    out_of_bounds_count = 0

    processed_vitals = {}
    for col in FEATURE_ORDER:
        val = patient_data.get(col)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            missing_count += 1
            imputed_features.append(col)
            imputed_val = feature_medians.get(col, 0.0)
            if col == "Gender":
                processed_vitals[col] = imputed_val
            else:
                processed_vitals[col] = float(imputed_val)
        elif col == "Gender":
            processed_vitals[col] = val
        else:
            try:
                num_val = float(val)
                if col in VALID_RANGES:
                    min_v, max_v = VALID_RANGES[col]
                    if not (min_v <= num_val <= max_v):
                        out_of_bounds_count += 1
                processed_vitals[col] = num_val
            except (ValueError, TypeError):
                missing_count += 1
                imputed_features.append(col)
                processed_vitals[col] = float(feature_medians.get(col, 0.0))

    # Input validation thresholds (allow up to 12 missing secondary fields for PDF extraction)
    if missing_count > 12:
        raise ValueError(f"Patient data rejected: Too many missing fields ({missing_count} missing out of 17).")
    if out_of_bounds_count > 3:
        raise ValueError(f"Patient data rejected: Multiple physiological values out of bounds ({out_of_bounds_count} invalid).")

    return processed_vitals, imputed_features

def _preprocess(patient_data):
    """
    Single shared preprocessing pipeline:
    Validate, impute medians, encode gender, scale features, and clip extreme outliers.
    """
    load_resources()
    vitals, imputed_features = _validate_and_impute(patient_data)
    
    numeric_encoded = {}
    for col in FEATURE_ORDER:
        val = vitals[col]
        if col == "Gender":
            if isinstance(val, str):
                val_clean = val.strip().capitalize()
                if val_clean in gender_encoder.classes_:
                    val_encoded = gender_encoder.transform([val_clean])[0]
                else:
                    val_encoded = 1 if val_clean.startswith("M") else 0
            else:
                val_encoded = int(val) if val is not None else 0
            numeric_encoded[col] = val_encoded
        else:
            numeric_encoded[col] = float(val)

    df_input = pd.DataFrame([numeric_encoded])[FEATURE_ORDER]
    X_scaled = scaler.transform(df_input)
    X_scaled = np.clip(X_scaled, -4.0, 4.0)
    df_scaled = pd.DataFrame(X_scaled, columns=FEATURE_ORDER)

    return df_scaled, vitals, imputed_features

def apply_clinical_safety_override(vitals, model_label, model_conf):
    """
    Clinical safety check: if core vitals are strictly normal, classify as Healthy.
    Returns (final_label, final_conf, overridden, override_reason).
    Does NOT overwrite confidence_score with artificial manufactured numbers.
    """
    is_healthy = True

    if vitals.get('Oxygen Saturation', 98.0) < 95.0:
        is_healthy = False
    if not (18.5 <= vitals.get('BMI', 22.0) <= 24.9):
        is_healthy = False
    if vitals.get('Blood Pressure', 110.0) >= 120.0:
        is_healthy = False
    if vitals.get('Glucose', 90.0) > 100.0:
        is_healthy = False
    if vitals.get('HbA1c', 5.0) >= 5.7:
        is_healthy = False

    if is_healthy and model_label != "Healthy":
        return "Healthy", model_conf, True, "Core clinical vitals (SpO2, BMI, BP, Glucose, HbA1c) are within normal health ranges."
    
    return model_label, model_conf, False, None

def make_prediction(patient_data):
    """
    Predict medical condition based on patient data dictionary with calibrated thresholds & audit logging.
    """
    load_resources()
    
    # Hash request data for privacy-preserving audit logging (No raw PHI written)
    data_str = str(sorted(patient_data.items()))
    req_hash = hashlib.sha256(data_str.encode()).hexdigest()[:12]

    df_scaled, vitals, imputed_features = _preprocess(patient_data)
    
    # Predict probabilities across 7 classes
    class_probabilities = model.predict_proba(df_scaled)[0]
    
    # Argmax lookup for exact class index
    predicted_class_idx = int(np.argmax(class_probabilities))
    raw_label = str(label_encoder.classes_[predicted_class_idx])
    raw_conf = float(class_probabilities[predicted_class_idx])

    # Apply clinical safety override layer
    final_label, final_conf, overridden, override_reason = apply_clinical_safety_override(vitals, raw_label, raw_conf)

    # Probabilities dictionary for all 7 conditions
    probabilities_dict = {
        str(label_encoder.classes_[i]): float(prob)
        for i, prob in enumerate(class_probabilities)
    }

    # Calibrated Risk Level Thresholds (7-class baseline = 14.28% chance):
    # High: >= 0.40 confidence, Moderate: >= 0.25 confidence, Low: < 0.25 confidence
    # -----------------------------------------------------------------------------------
    # CLINICAL PRECAUTION POLICY (CANCER ASYMMETRIC THRESHOLD):
    # Cancer is assigned "High Risk" at confidence >= 0.25 (vs. >= 0.40 for all other conditions).
    # RATIONALE: Cancer is a high-stakes, life-threatening condition where a false negative 
    # (under-triaging potential malignancy) is clinically far more dangerous than a false positive. 
    # Lowering the threshold to 0.25 (just above random 14.28% baseline chance) ensures potential 
    # cancer indicators receive immediate clinical attention. This is a deliberate policy decision,
    # not a bug or leftover threshold. No other class uses an asymmetric threshold.
    # -----------------------------------------------------------------------------------
    if final_label == "Healthy":
        risk_level = "Low"
    elif final_label == "Cancer" and final_conf >= 0.25:
        risk_level = "High"
    else:
        if final_conf >= 0.40:
            risk_level = "High"
        elif final_conf >= 0.25:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

    # Privacy-safe audit log (No PHI written)
    logger.info(f"ReqID:{req_hash} | Outcome:{final_label} | Conf:{final_conf:.3f} | Risk:{risk_level} | Overridden:{overridden}")

    core_imputed = [f for f in imputed_features if f in CORE_VITALS]
    warning_msg = None
    if len(core_imputed) >= 2:
        warning_msg = "Low confidence: Multiple core clinical vitals were estimated."

    if final_label == "Arthritis":
        arthritis_warning = "Note: Arthritis predictions have lower historical recall (64.35%) and should be treated as lower-confidence."
        if warning_msg:
            warning_msg += " | " + arthritis_warning
        else:
            warning_msg = arthritis_warning

    return {
        "prediction": final_label,
        "confidence_score": final_conf,
        "risk_level": risk_level,
        "probability": final_conf,
        "probabilities": probabilities_dict,
        "overridden": overridden,
        "override_reason": override_reason,
        "raw_model_prediction": raw_label,
        "raw_model_confidence": raw_conf,
        "imputed_features": imputed_features,
        "imputed_count": len(imputed_features),
        "extracted_count": len(FEATURE_ORDER) - len(imputed_features),
        "warning": warning_msg
    }

def get_shap_explanation(patient_data):
    """Generates an exact TreeSHAP waterfall plot styled to match the warm cream theme."""
    load_resources()
    df_scaled, _, _ = _preprocess(patient_data)
    
    class_probabilities = model.predict_proba(df_scaled)[0]
    predicted_class_idx = int(np.argmax(class_probabilities))

    # Fast & exact TreeExplainer for Tree Ensemble / Random Forest
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(df_scaled)

    plt.clf()
    fig = plt.figure(figsize=(8, 4.8), facecolor='#FBF8F0')
    try:
        if len(shap_values.shape) == 3:
            shap.plots.waterfall(shap_values[0, :, predicted_class_idx], show=False)
        else:
            shap.plots.waterfall(shap_values[0], show=False)
    except Exception:
        plt.clf()
        if len(shap_values.shape) == 3:
            shap.plots.bar(shap_values[0, :, predicted_class_idx], show=False)
        else:
            shap.plots.bar(shap_values[0], show=False)

    # Recolor plot elements to match warm cream / editorial theme
    ax = plt.gca()
    fig = plt.gcf()
    fig.patch.set_facecolor('#FBF8F0')
    ax.set_facecolor('#FBF8F0')

    # Recolor bars: #7A1F2B for positive impact, #7C8B7A for negative impact
    for patch in ax.patches:
        w = patch.get_width()
        if w >= 0:
            patch.set_facecolor('#7A1F2B')
        else:
            patch.set_facecolor('#7C8B7A')

    # Recolor text, ticks, and hairline spines
    for text in ax.texts:
        text.set_color('#2B2420')
        text.set_fontsize(9)
    ax.tick_params(colors='#2B2420', labelsize=9)
    for spine in ax.spines.values():
        spine.set_color('#D9CFC0')
        spine.set_linewidth(1.0)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor='#FBF8F0')
    plt.close()
    buf.seek(0)
    
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_b64
