import csv
from datetime import datetime
import pandas as pd

clean_data = []
event_lookup = {}

with open("frc-events.csv", "r") as file:
    for row in csv.DictReader(file):
        event_lookup[f"{row['code']}_{row['year']}"] = {
            "event_date": datetime.strptime(row["dateStart"], "%Y-%m-%dT%H:%M:%S"),
            "week": int(row["weekNumber"]),
        }

tournament_level_lookup = {"Qualification": 1, "Playoff": 2}


to_int = ["year", "matchNumber"]
to_float = [
    "Blue1",
    "Blue2",
    "Blue3",
    "Red1",
    "Red2",
    "Red3",
    "scoreBlueAuto",
    "scoreBlueFinal",
    "scoreBlueFoul",
    "scoreRedAuto",
    "scoreRedFinal",
    "scoreRedFoul",
]
to_bool = [
    "Blue1_dq",
    "Blue2_dq",
    "Blue3_dq",
    "Red1_dq",
    "Red2_dq",
    "Red3_dq",
    "isReplay",
]
to_datetime = ["actualStartTime", "autoStartTime", "postResultTime"]

with open("frc-api-data.csv", "r") as file:
    for row in csv.DictReader(file):
        if int(row["matchNumber"]) < 900:
            # Clean up the ints
            for k in to_int:
                try:
                    row[k] = int(row[k])
                except:
                    row[k] = None
            # Clean up the floats
            for k in to_float:
                try:
                    row[k] = float(row[k])
                except:
                    row[k] = None
            # Clean up the bools
            for k in to_bool:
                row[k] = row[k] == "True"
            # Clean up the datetimes
            for k in to_datetime:
                try:
                    row[k] = datetime.strptime(row[k], "%Y-%m-%dT%H:%M:%S")
                except:
                    row[k] = None
            # Add in the tournament sort
            row["sort"] = tournament_level_lookup[row["tournamentLevel"]]
            # Add in event sorting data
            event_data = event_lookup[f"{row['event_code']}_{row['year']}"]
            row = {**row, **event_data}

            clean_data.append(row)

clean_data = pd.DataFrame(clean_data)
clean_data = (
    clean_data.sort_values(
        by=["year", "week", "event_date", "event_code", "sort", "matchNumber"],
        ascending=[True, True, True, True, True, True],
    )
    .drop("sort", axis=1)
    .reset_index(drop=True)
    .reset_index()
)

clean_data.to_csv("clean-frc-data.csv", index=False)
