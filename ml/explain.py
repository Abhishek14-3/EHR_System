import os
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# Configuration
# ==========================================

MODEL_PATH = "ml/models/best_model.pkl"
DATA_PATH = "ml/data/cleaned_healthcare_data.csv"
PLOT_DIR = "ml/plots"

os.makedirs(PLOT_DIR, exist_ok=True)

# ==========================================
# Load Model
# ==========================================

print("\nLoading trained model...")

model = joblib.load(MODEL_PATH)

# ==========================================
# Load Dataset
# ==========================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

X = df.drop("Medical Condition", axis=1)

print(f"Dataset Shape : {X.shape}")

# ==========================================
# Create SHAP Explainer
# ==========================================

print("\nCreating SHAP Explainer...")

explainer = shap.Explainer(model, X)

print("Calculating SHAP values...")

shap_values = explainer(X)

print("Completed.")

# ==========================================
# SHAP Summary Plot
# ==========================================

print("\nGenerating Summary Plot...")

plt.figure()

shap.summary_plot(
    shap_values,
    X,
    show=False
)

plt.tight_layout()

plt.savefig(
    f"{PLOT_DIR}/shap_summary.png",
    dpi=300
)

plt.close()

# ==========================================
# SHAP Bar Plot
# ==========================================

print("Generating Feature Importance Plot...")

plt.figure()

shap.plots.bar(
    shap_values,
    show=False
)

plt.tight_layout()

plt.savefig(
    f"{PLOT_DIR}/shap_bar.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# Top Features
# ==========================================

importance = abs(shap_values.values).mean(axis=0)

feature_importance = pd.DataFrame({

    "Feature": X.columns,

    "Importance": importance

})

feature_importance = feature_importance.sort_values(

    by="Importance",

    ascending=False

)

feature_importance.to_csv(

    "ml/reports/shap_feature_importance.csv",

    index=False

)

print("\nTop 10 Important Features")

print(feature_importance.head(10))

print("\n===================================")
print("SHAP ANALYSIS COMPLETED")
print("===================================")

print("\nGenerated Files")

print("✓ shap_summary.png")

print("✓ shap_bar.png")

print("✓ shap_feature_importance.csv")