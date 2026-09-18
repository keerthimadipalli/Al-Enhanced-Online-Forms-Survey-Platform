"""
ML/train_model.py
Decision Tree model to predict survey response category
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# ─── Dataset ──────────────────────────────────────────────────────────────────
# Columns:
#   form_type       : type of survey (feedback, event, quiz, registration, research)
#   num_questions   : number of questions in the form
#   num_responses   : total responses collected
#   avg_ans_length  : average character length of text answers
#   submission_hour : hour of day when submitted (0–23)
#   label           : 0=Negative, 1=Neutral, 2=Positive

np.random.seed(42)
n = 300

form_types = np.random.choice(['feedback', 'event', 'quiz', 'registration', 'research'], n)
num_questions = np.random.randint(3, 15, n)
num_responses = np.random.randint(1, 100, n)
avg_ans_length = np.random.randint(5, 150, n)
submission_hour = np.random.randint(0, 24, n)

# Labels based on some logic + noise
labels = []
for i in range(n):
    score = 0
    if avg_ans_length[i] > 60: score += 1       # detailed = engaged = positive
    if num_responses[i] > 30: score += 1        # many responses = popular = positive
    if num_questions[i] < 6: score += 1         # short form = easy = positive
    if submission_hour[i] in range(9, 21): score += 1  # business hours = engaged
    if avg_ans_length[i] < 15: score -= 1       # very short = disengaged
    noise = np.random.randint(-1, 2)
    score += noise
    if score >= 3: labels.append(2)
    elif score >= 1: labels.append(1)
    else: labels.append(0)

# Encode form_type
le = LabelEncoder()
form_type_enc = le.fit_transform(form_types)

df = pd.DataFrame({
    'form_type': form_type_enc,
    'num_questions': num_questions,
    'num_responses': num_responses,
    'avg_ans_length': avg_ans_length,
    'submission_hour': submission_hour,
    'label': labels
})

print("Dataset shape:", df.shape)
print("Label distribution:\n", df['label'].value_counts())
print(df.head())

# ─── Split ────────────────────────────────────────────────────────────────────
X = df.drop('label', axis=1)
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

# ─── Train ────────────────────────────────────────────────────────────────────
clf = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42
)
clf.fit(X_train, y_train)

# ─── Evaluate ─────────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {acc:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Negative", "Neutral", "Positive"]))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nFeature Importances:")
for feat, imp in zip(X.columns, clf.feature_importances_):
    print(f"  {feat}: {imp:.3f}")

# ─── Save ─────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(__file__), exist_ok=True)
joblib.dump(clf, os.path.join(os.path.dirname(__file__), "model.pkl"))
df.to_csv(os.path.join(os.path.dirname(__file__), "survey_dataset.csv"), index=False)
print("\nModel saved to ML/model.pkl")
print("Dataset saved to ML/survey_dataset.csv")
