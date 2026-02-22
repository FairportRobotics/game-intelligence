from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import lightgbm as lgbm
import pickle

model_type = "nb"  # Change this to "rf", "nb", "mlp", or "svm" as needed

# Read in the data
data = pd.read_csv("full_data.csv")

# data = data.loc[data['level'] != "Other"] # Filter out 'Other' class for binary classification

X = data.drop(["level"], axis=1)  # Features

# data.loc[data['level'] != "Other", 'level'] = "Contender"
y = data["level"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

if model_type == "lgbm":
    model = lgbm.LGBMClassifier(
        objective="multiclass",
        num_class=len(np.unique(y)),  # Explicitly state the number of classes
        n_estimators=100,
        learning_rate=0.05,
        random_state=42,
        # Other parameters can be tuned as needed (e.g., num_leaves, max_depth))
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgbm.early_stopping(10)],  # Stop if no improvement in 10 rounds
    )
else:
    # Train the model
    if model_type == "rf":
        model = RandomForestClassifier(class_weight="balanced", random_state=42)
    elif model_type == "nb":
        model = GaussianNB()
    elif model_type == "mlp":
        model = MLPClassifier(random_state=42, max_iter=1000)
    elif model_type == "svm":
        model = make_pipeline(StandardScaler(), SVC(gamma="auto"))

    model.fit(X_train, y_train)


with open(f"models/{model_type}_3_class.pkl", "wb") as f:
    pickle.dump(model, f)

# Evaluate the model
y_pred = model.predict(X_test)

print("Classification Report:")
# Use the classification_report to see per-class metrics
print(classification_report(y_test, y_pred))

"""
preds_df = pd.DataFrame(
    y_pred,
    columns=["predicted_level"],
    index=X_test.index
)

probs = model.predict_proba(X_test)
probs_df = pd.DataFrame(
    probs, 
    columns=model.classes_, 
    index=X_test.index
)

probs_df = probs_df.join(preds_df).reset_index()
#probs_df = probs_df.join(X_test)
probs_df.to_csv(f'{model_type}_3_class_predicted_probabilities.csv', index=False)
#X_test = X_test.join(y_test).reset_index()
#X_test.to_csv("data.csv", index=False)
#"""
