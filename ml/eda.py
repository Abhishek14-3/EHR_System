import os
import logging
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Configuration
# -----------------------------
DATASET_PATH = "ml/data/healthcare_risk_raw.csv"
PLOTS_DIR = "ml/plots"
REPORTS_DIR = "ml/reports"

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# Load Dataset
# -----------------------------
def load_dataset():
    try:
        df = pd.read_csv(DATASET_PATH)
        logging.info("Dataset loaded successfully.")
        return df
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")
        raise


# -----------------------------
# Dataset Summary
# -----------------------------
def dataset_summary(df):
    print("\n==============================")
    print(" HEALTHCHAIN DATASET SUMMARY")
    print("==============================")

    print(f"\nRows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    return {
        "rows": df.shape[0],
        "columns": df.shape[1]
    }


# -----------------------------
# Missing Values
# -----------------------------
def missing_values(df):

    missing = df.isnull().sum()

    print("\nMissing Values")
    print(missing)

    plt.figure(figsize=(10,5))
    missing.plot(kind="bar")
    plt.title("Missing Values")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/missing_values.png")
    plt.close()

    return missing


# -----------------------------
# Duplicate Rows
# -----------------------------
def duplicate_rows(df):

    duplicates = df.duplicated().sum()

    print(f"\nDuplicate Rows : {duplicates}")

    return duplicates


# -----------------------------
# Numerical & Categorical
# -----------------------------
def feature_types(df):

    numerical = df.select_dtypes(include=["int64","float64"]).columns.tolist()

    categorical = df.select_dtypes(include=["object"]).columns.tolist()

    print("\nNumerical Features")
    print(numerical)

    print("\nCategorical Features")
    print(categorical)

    return numerical, categorical


# -----------------------------
# Class Distribution
# -----------------------------
def class_distribution(df):

    target = "Medical Condition"

    if target not in df.columns:
        print("\nTarget column not found.")
        return

    counts = df[target].value_counts()

    print("\nMedical Condition Distribution")
    print(counts)

    plt.figure(figsize=(8,5))
    counts.plot(kind="bar")
    plt.title("Medical Condition Distribution")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/class_distribution.png")
    plt.close()


# -----------------------------
# Correlation
# -----------------------------
def correlation(df):

    numeric = df.select_dtypes(include=["int64","float64"])

    corr = numeric.corr()

    plt.figure(figsize=(12,10))
    plt.imshow(corr, cmap="coolwarm", aspect="auto")
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/correlation_heatmap.png")
    plt.close()


# -----------------------------
# Distribution Plots
# -----------------------------
def plot_distribution(df, column):

    if column not in df.columns:
        return

    plt.figure(figsize=(6,4))
    df[column].hist(bins=30)
    plt.title(column)
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/{column}.png")
    plt.close()


# -----------------------------
# Report
# -----------------------------
def save_report(summary,
                missing,
                duplicates,
                numerical,
                categorical):

    report = f"""
===============================
HEALTHCHAIN DATASET REPORT
===============================

Rows : {summary['rows']}
Columns : {summary['columns']}

Duplicate Rows :
{duplicates}

Missing Values
{missing}

Numerical Features
{numerical}

Categorical Features
{categorical}

Recommended Columns To Remove

random_notes
noise_col

===============================
"""

    with open(f"{REPORTS_DIR}/eda_report.txt","w") as f:
        f.write(report)


# -----------------------------
# Main
# -----------------------------
def main():

    df = load_dataset()

    summary = dataset_summary(df)

    missing = missing_values(df)

    duplicates = duplicate_rows(df)

    numerical, categorical = feature_types(df)

    class_distribution(df)

    correlation(df)

    plot_distribution(df,"Age")
    plot_distribution(df,"BMI")
    plot_distribution(df,"Blood Pressure")
    plot_distribution(df,"Cholesterol")

    save_report(
        summary,
        missing,
        duplicates,
        numerical,
        categorical
    )

    print("\nEDA Completed Successfully")


if __name__ == "__main__":
    main()