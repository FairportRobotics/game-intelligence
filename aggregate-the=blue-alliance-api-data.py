# This script aggregates up all the data pulled from the blue alliance API

from glob import glob
import pandas as pd

all_data = []

for file_path in glob("the-blue-alliance-api-data/*.csv"):
    print(file_path)
    df = pd.read_csv(file_path)
    for row in df.to_dict(orient="records"):
        all_data.append(row)

df = pd.DataFrame(all_data)
# Let's alphabetize the columns
df = df[sorted(df)]
# We want some to be at the begining of the data
cols = ["year", "event_key", "event_start_date", "event_end_date", "match_key"]
# Add in all the remaining columns in alphabetical order
for col in [col for col in df.columns if col not in cols]:
    cols.append(col)
# Reorder the columns
df = df[cols]
# Save the data off
df.to_csv("the-blue-alliance-api-data.csv", index=False)