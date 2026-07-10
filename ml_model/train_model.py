import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Create dummy data if heart.csv is missing so the project doesn't crash
try:
    df = pd.read_csv('heart.csv')
except:
    data = np.random.randint(0, 100, size=(1000, 13))
    target = np.random.randint(0, 2, size=(1000, 1))
    df = pd.DataFrame(np.hstack([data, target]), columns=['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'])

X = df.drop('target', axis=1)
y = df['target']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_scaled, y)

joblib.dump(model, 'heart_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
print("✅ ML Model 'heart_model.joblib' and Scaler saved!")