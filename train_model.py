"""Synthetic-data demonstration only. Labels are generated from a simple rule, not real students."""
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

rng = np.random.default_rng(42)
n = 500
data = pd.DataFrame({
    "attendance": rng.uniform(35, 100, n),
    "marks": rng.uniform(20, 100, n),
    "assignment_score": rng.uniform(25, 100, n),
})
# This rule defines synthetic labels and therefore does not demonstrate real-world predictive validity.
y = ((data.attendance < 65) | (data.marks < 45) | (data.assignment_score < 40)).astype(int)
X_train, X_test, y_train, y_test = train_test_split(data, y, test_size=0.25, random_state=42, stratify=y)
model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)
print(classification_report(y_test, model.predict(X_test), zero_division=0))
Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/risk_model.joblib")
print("Saved models/risk_model.joblib (synthetic-data demo only)")
