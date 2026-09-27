import os
import joblib
import logging
import pandas as pd

from sklearn.preprocessing import LabelEncoder, StandardScaler

# ==========================================================
# Configuration
# ==========================================================

DATA_PATH = "ml/data/healthcare_risk_raw.csv"

MODELS_DIR = "ml/models"
REPORTS_DIR = "ml/reports"
DATA_DIR = "ml/data"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================================
# Load Dataset
# ==========================================================

def load_dataset():

    logging.info("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    return df


# ==========================================================
# Remove Unnecessary Columns
# ==========================================================

def remove_unused_columns(df):

    print("\nRemoving unnecessary columns...")

    columns_to_remove = [
        "random_notes",
        "noise_col"
    ]

    removed = []

    for col in columns_to_remove:
        if col in df.columns:
            df.drop(columns=col, inplace=True)
            removed.append(col)

    print("Removed:", removed)

    return df


# ==========================================================
# Handle Missing Values
# ==========================================================

def handle_missing_values(df):

    print("\nHandling missing values...")

    # Drop rows where target is missing

    before = len(df)

    df = df.dropna(subset=["Medical Condition"]).copy()

    after = len(df)

    print(f"Dropped {before-after} rows (missing target).")

    # Numerical columns

    numerical_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    for column in numerical_columns:

        df.loc[:, column] = df[column].fillna(df[column].median())

    # Gender

    if "Gender" in df.columns:

       df.loc[:, "Gender"] = df["Gender"].fillna(df["Gender"].mode()[0])
        

    return df


# ==========================================================
# Encode Categorical Features
# ==========================================================

def encode_features(df):

    print("\nEncoding categorical features...")

    gender_encoder = LabelEncoder()

    df["Gender"] = gender_encoder.fit_transform(df["Gender"])

    label_encoder = LabelEncoder()

    df["Medical Condition"] = label_encoder.fit_transform(
        df["Medical Condition"]
    )

    joblib.dump(
        gender_encoder,
        f"{MODELS_DIR}/gender_encoder.pkl"
    )

    joblib.dump(
        label_encoder,
        f"{MODELS_DIR}/label_encoder.pkl"
    )

    print("Encoders saved.")

    return df


# ==========================================================
# Feature Scaling
# ==========================================================

def scale_features(df):

    print("\nScaling numerical features...")

    X = df.drop(columns=["Medical Condition"])

    y = df["Medical Condition"]

    numerical_columns = X.select_dtypes(
        include=["int64", "float64"]
    ).columns

    scaler = StandardScaler()

    X[numerical_columns] = scaler.fit_transform(
        X[numerical_columns]
    )

    joblib.dump(
        scaler,
        f"{MODELS_DIR}/scaler.pkl"
    )

    joblib.dump(
        list(X.columns),
        f"{MODELS_DIR}/feature_columns.pkl"
    )

    print("Scaler saved.")

    processed = X.copy()

    processed["Medical Condition"] = y

    return processed


# ==========================================================
# Save Clean Dataset
# ==========================================================

def save_dataset(df):

    output_path = f"{DATA_DIR}/cleaned_healthcare_data.csv"

    df.to_csv(
        output_path,
        index=False
    )

    print("\nClean dataset saved.")

    return output_path


# ==========================================================
# Generate Report
# ==========================================================

def generate_report(df):

    report = f"""
==========================================
HEALTHCHAIN PREPROCESSING REPORT
==========================================

Rows After Cleaning : {df.shape[0]}

Columns : {df.shape[1]}

Features

{list(df.columns)}

Target

Medical Condition

Scaling

StandardScaler

Encoding

Gender -> LabelEncoder

Medical Condition -> LabelEncoder

Saved Files

gender_encoder.pkl

label_encoder.pkl

scaler.pkl

feature_columns.pkl

==========================================
"""

    with open(
        f"{REPORTS_DIR}/preprocessing_report.txt",
        "w"
    ) as file:

        file.write(report)

    print("\nReport generated.")


# ==========================================================
# Main
# ==========================================================

def main():

    print("\n===================================")
    print(" HEALTHCHAIN PREPROCESSING")
    print("===================================")

    df = load_dataset()

    df = remove_unused_columns(df)

    df = handle_missing_values(df)

    df = encode_features(df)

    df = scale_features(df)

    path = save_dataset(df)

    generate_report(df)

    print("\n===================================")
    print("PREPROCESSING COMPLETED")
    print("===================================")

    print(f"\nClean Dataset : {path}")

    print("\nSaved Models")

    print("✓ scaler.pkl")

    print("✓ label_encoder.pkl")

    print("✓ gender_encoder.pkl")

    print("✓ feature_columns.pkl")


if __name__ == "__main__":
    main()