import os
import joblib
import logging
import warnings
import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from sklearn.model_selection import cross_val_score

import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

# =====================================================
# Configuration
# =====================================================

DATASET_PATH = "ml/data/cleaned_healthcare_data.csv"

MODEL_DIR = "ml/models"
REPORT_DIR = "ml/reports"
PLOT_DIR = "ml/plots"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =====================================================
# Load Dataset
# =====================================================

def load_dataset():

    logging.info("Loading cleaned dataset...")

    df = pd.read_csv(DATASET_PATH)

    X = df.drop("Medical Condition", axis=1)

    y = df["Medical Condition"]

    return X, y


# =====================================================
# Train Test Split
# =====================================================

def split_dataset(X, y):

    logging.info("Splitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y

    )

    print("\nTraining Samples :", len(X_train))
    print("Testing Samples  :", len(X_test))

    return X_train, X_test, y_train, y_test


# =====================================================
# Initialize Models
# =====================================================

def initialize_models():

    models = {

        "Logistic Regression":

            LogisticRegression(
                max_iter=2000,
                random_state=42
            ),

        "Decision Tree":

            DecisionTreeClassifier(
                random_state=42
            ),

        "Random Forest":

            RandomForestClassifier(

                n_estimators=300,

                random_state=42

            ),

        "Extra Trees":

            ExtraTreesClassifier(

                n_estimators=300,

                random_state=42

            ),

        "Gradient Boosting":

            GradientBoostingClassifier(

                random_state=42

            )

    }

    return models


# =====================================================
# Train Models
# =====================================================

def train_models(
        models,
        X_train,
        y_train
):
    from sklearn.utils.class_weight import compute_sample_weight
    
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
    
    trained_models = {}

    print("\n==============================")
    print("TRAINING MODELS")
    print("==============================")

    for name, model in models.items():

        print(f"\nTraining {name} ...")

        model.fit(
            X_train,
            y_train,
            sample_weight=sample_weights
        )

        trained_models[name] = model

        print("Completed")

    return trained_models

# =====================================================
# Evaluate Models
# =====================================================

def evaluate_models(trained_models, X_test, y_test):

    results = []

    best_accuracy = 0
    best_model = None
    best_name = ""

    print("\n==============================")
    print("MODEL EVALUATION")
    print("==============================")

    for name, model in trained_models.items():

        predictions = model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)

        precision = precision_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        )

        recall = recall_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        )

        cv_score = cross_val_score(
            model,
            X_test,
            y_test,
            cv=5
        ).mean()

        print(f"\n{name}")
        print(f"Accuracy  : {accuracy:.4f}")
        print(f"Precision : {precision:.4f}")
        print(f"Recall    : {recall:.4f}")
        print(f"F1 Score  : {f1:.4f}")
        print(f"CV Score  : {cv_score:.4f}")

        results.append({
            "Model": name,
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "CV Score": cv_score
        })

        if accuracy > best_accuracy:

            best_accuracy = accuracy
            best_model = model
            best_name = name

    print("\n=================================")
    print("BEST MODEL")
    print("=================================")

    print(best_name)
    print(f"Accuracy : {best_accuracy:.4f}")

    return results, best_model, best_name
# =====================================================
# Save Best Model
# =====================================================

def save_best_model(model):

    joblib.dump(
        model,
        f"{MODEL_DIR}/best_model.pkl"
    )

    print("\nBest model saved.")
    
    # =====================================================
# Save Comparison CSV
# =====================================================

def save_results(results):

    df = pd.DataFrame(results)

    df.to_csv(
        f"{REPORT_DIR}/model_comparison.csv",
        index=False
    )

    print("Comparison report saved.")
    
    # =====================================================
# Accuracy Plot
# =====================================================

def plot_accuracy(results):

    df = pd.DataFrame(results)

    plt.figure(figsize=(10,6))

    plt.bar(
        df["Model"],
        df["Accuracy"]
    )

    plt.xticks(rotation=20)

    plt.ylabel("Accuracy")

    plt.title("Model Accuracy Comparison")

    plt.tight_layout()

    plt.savefig(
        f"{PLOT_DIR}/accuracy_comparison.png"
    )

    plt.close()

    print("Accuracy graph saved.")
    
# =====================================================
# Main
# =====================================================

def main():

    print("\n====================================")
    print(" HEALTHCHAIN MODEL TRAINING ")
    print("====================================")

    X, y = load_dataset()

    X_train, X_test, y_train, y_test = split_dataset(X, y)

    models = initialize_models()

    trained_models = train_models(
        models,
        X_train,
        y_train
    )

    results, best_model, best_name = evaluate_models(
        trained_models,
        X_test,
        y_test
    )

    save_best_model(best_model)

    save_results(results)

    plot_accuracy(results)

    print("\n====================================")
    print("TRAINING COMPLETED")
    print("====================================")

    print(f"\nBest Model : {best_name}")

if __name__ == "__main__":
    main()