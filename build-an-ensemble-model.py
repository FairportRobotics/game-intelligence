import numpy as np
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    StackingClassifier,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, classification_report
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
import pandas as pd
import pickle
import joblib

# Load dataset
data = pd.read_csv("full_data.csv")

# data = data.loc[data['level'] != "Other"] # Filter out 'Other' class for binary classification

X = data.drop(["level"], axis=1)  # Features

# data.loc[data['level'] != "Other", 'level'] = "Contender"
y = data["level"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Base learners
estimators = [
    # Tree-based models (no scaling needed)
    ("rf", RandomForestClassifier(n_estimators=100, random_state=42)),
    ("lgbm", LGBMClassifier(n_estimators=100, random_state=42)),
    ("xgb", XGBClassifier(n_estimators=100, eval_metric="logloss", random_state=42)),
    # Probabilistic model
    ("gnb", GaussianNB()),
    # Models that benefit from scaling
    (
        "mlp",
        make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(100,), max_iter=1000, random_state=42),
        ),
    ),
]

# Meta-learner
meta_model = LogisticRegression(max_iter=1000)

stacking_clf = StackingClassifier(
    estimators=estimators,
    final_estimator=meta_model,
    stack_method="predict_proba",
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    n_jobs=-1,
)

pipeline = Pipeline(steps=[("model", stacking_clf)])

param_dist = {
    # Random Forest
    "model__rf__n_estimators": [100, 200, 300],
    "model__rf__max_depth": [None, 5, 10],
    # XGBoost
    "model__xgb__n_estimators": [100, 200],
    "model__xgb__max_depth": [3, 5, 7],
    # LightGBM
    "model__lgbm__n_estimators": [100, 200],
    "model__lgbm__num_leaves": [31, 63],
    # MLP
    "model__mlp__mlpclassifier__hidden_layer_sizes": [(100,), (100, 50)],
    "model__mlp__mlpclassifier__alpha": [0.0001, 0.001],
    # Meta-model
    "model__final_estimator__C": [0.1, 1.0, 10.0],
}

random_search = RandomizedSearchCV(
    pipeline,
    param_distributions=param_dist,
    n_iter=5,  # adjust for compute budget
    scoring="accuracy",
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1,
)

random_search.fit(X_train, y_train)
model = random_search.best_estimator_

joblib.dump(model, "models/ensemble_3_class.pkl")

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
# Use the classification_report to see per-class metrics
print(classification_report(y_test, y_pred))
