import pandas as pd
import os
import sqlite3
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

def split_data(df, random_state, train_size=0.6, val_size=0.2, test_size=0.2, shuffle=True):
    """Splits a DataFrame into train, validation, and test sets."""
    if train_size + val_size + test_size != 1:
        raise ValueError("Sizes must add up to 1")

    train_df, temp_df = train_test_split(df, test_size=(1 - train_size), random_state=random_state, shuffle=shuffle)
    val_df, test_df = train_test_split(temp_df, test_size=(test_size / (val_size + test_size)), random_state=random_state, shuffle=shuffle)

    return train_df, val_df, test_df

db = sqlite3.connect('the-blue-alliance.db')
cursor = db.cursor()

df = pd.read_sql_query('SELECT * FROM crystal_ball', db)
# Drop the id column
df = df.drop(columns=['id'])
# Split into train test validation datasets using a 60/20/20 split
train_df, val_df, test_df = split_data(df, random_state=int(os.environ.get('RANDOM_STATE')))
# Save the dataframes to csv files
train_df.to_csv('train.csv', index=False)
val_df.to_csv('val.csv', index=False)
test_df.to_csv('test.csv', index=False)