import os
import joblib
import pandas as pd

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV
)
from sklearn.metrics import accuracy_score

# ===============================
# Load Dataset
# ===============================

df = pd.read_csv("ml/data/cleaned_healthcare_data.csv")

X = df.drop("Medical Condition", axis=1)
y = df["Medical Condition"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ===============================
# Parameter Grid
# ===============================

params = {

    "n_estimators":[100,200,300,400],

    "learning_rate":[0.01,0.05,0.1],

    "max_depth":[2,3,4,5],

    "min_samples_split":[2,5,10],

    "min_samples_leaf":[1,2,4],

    "subsample":[0.8,0.9,1.0]

}

# ===============================
# Search
# ===============================

print("\nSearching best parameters...\n")

search = RandomizedSearchCV(

    GradientBoostingClassifier(),

    param_distributions=params,

    n_iter=25,

    cv=5,

    scoring="accuracy",

    n_jobs=-1,

    random_state=42

)

search.fit(X_train,y_train)

# ===============================
# Results
# ===============================

best_model = search.best_estimator_

predictions = best_model.predict(X_test)

accuracy = accuracy_score(y_test,predictions)

print("="*50)

print("BEST PARAMETERS")

print(search.best_params_)

print("="*50)

print(f"Accuracy : {accuracy:.4f}")

# ===============================
# Save
# ===============================

os.makedirs("ml/models",exist_ok=True)

joblib.dump(

    best_model,

    "ml/models/best_model.pkl"

)

print("\nOptimized model saved.")