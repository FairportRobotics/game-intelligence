# This script aggregates up all the data pulled from the blue alliance API

from glob import glob
import pandas as pd

all_data = []

for file_path in glob("frc-api-data/*.csv"):
    print(file_path)
    year = file_path.replace(".csv", "").replace("frc-api-data", "")[-4:]
    df = pd.read_csv(file_path)
    for row in df.to_dict(orient="records"):
        row["year"] = int(year)
        all_data.append(row)

df = pd.DataFrame(all_data)
# Let's alphabetize the columns
df = df[sorted(df)]
# We want some to be at the begining of the data
cols = [
    "event_code",
    "year",
    "description",
    "tournamentLevel",
    "matchNumber",
    "matchVideoLink",
    "actualStartTime",
    "autoStartTime",
    "postResultTime",
    "isReplay",
]
# Add in all the remaining columns in alphabetical order
for col in [col for col in df.columns if col not in cols]:
    cols.append(col)
# Reorder the columns
df = df[cols]
# Save the data off
df.to_csv("frc-api-data.csv", index=False)
