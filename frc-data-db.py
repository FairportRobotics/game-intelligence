import sqlite3
import pandas as pd

conn = sqlite3.connect('frc-data.db') 

# Create a cursor object
cursor = conn.cursor()

data = {"event":"frc-events.csv", "team":"frc-team-data.csv", "data":"clean-frc-data.csv"}

for t,f in data.items():
    df = pd.read_csv(f, low_memory=False)
    if "index" in df.columns:
        df.drop('index', axis=1, inplace=True)
    df.to_sql(name=t, con=conn)