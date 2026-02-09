from sklearn.ensemble import RandomForestClassifier
#from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
import lightgbm as lgbm

# Read in the data
data = pd.read_csv('full_data.csv')
X = data.drop(['level'], axis=1) # Features
y = data['level'] 

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train a Random Forest Classifier with balanced class weights
#model = RandomForestClassifier(class_weight='balanced', random_state=42)
#model = GaussianNB()
#model = MLPClassifier(random_state=42, max_iter=1000)
model = lgbm.LGBMClassifier(
    objective='multiclass',
    num_class=len(np.unique(y)), # Explicitly state the number of classes
    n_estimators=100,
    learning_rate=0.05,
    random_state=42,
    # Other parameters can be tuned as needed (e.g., num_leaves, max_depth)
)
#model.fit(X_train, y_train)
model.fit(X_train, y_train,
          eval_set=[(X_test, y_test)],
          callbacks=[lgbm.early_stopping(10)] # Stop if no improvement in 10 rounds
         )

# Evaluate the model using balanced accuracy and classification report
y_pred = model.predict(X_test)
print("Classification Report:")
# Use the classification_report to see per-class metrics
print(classification_report(y_test, y_pred)) 
