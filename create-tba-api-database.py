from glob import glob
import sqlite3
import json
import pandas as pd

conn = sqlite3.connect("trueskill.db")
cursor = conn.cursor()
comp_levels = {"qm": 1, "ef": 2, "qf": 3, "sf": 4, "f": 5}

cursor.execute('DROP TABLE IF EXISTS "tba_events"')
cursor.execute(
    'CREATE TABLE "tba_events" ( id INTEGER PRIMARY KEY, "key" TEXT UNIQUE, "name" TEXT, "short_name" TEXT, "event_code" TEXT, "start_date" TEXT, "year" INTEGER, "week" REAL, "address" TEXT, "city" TEXT, "state_prov" TEXT, "country" TEXT, "postal_code" TEXT )'
)
cursor.execute('DROP TABLE IF EXISTS "tba_matches"')
cursor.execute(
    'CREATE TABLE "tba_matches" ( id INTEGER PRIMARY KEY, "key" TEXT, "event_key" TEXT, "match_number" INTEGER, "comp_level" TEXT, "set_number" INTEGER, "winning_alliance" TEXT, "blue_score" INTEGER, "blue_team_1" TEXT, "blue_team_2" TEXT, "blue_team_3" TEXT, "blue_team_4" TEXT, "red_score" INTEGER, "red_team_1" TEXT, "red_team_2" TEXT, "red_team_3" TEXT, "red_team_4" TEXT )'
)
conn.commit()

tba_events_columns = [
    "key",
    "name",
    "short_name",
    "event_code",
    "start_date",
    "year",
    "week",
    "address",
    "city",
    "state_prov",
    "country",
    "postal_code",
]
for file_path in sorted(glob("raw_data/tba_events/*.json")):
    # print(file_path)
    with open(file_path, "r") as json_file:
        # data = json.load(json_file)
        data = pd.read_json(json_file)[tba_events_columns].sort_values(by="start_date")
        # print(data.columns)
        data.to_sql("tba_events", conn, if_exists="append", index=False)
        conn.commit()

data = []
for file_path in sorted(glob("raw_data/tba_matches/*.json")):
    # print(file_path)
    with open(file_path, "r") as json_file:
        for temp in json.load(json_file):
            row = {
                "key": temp["key"],
                "event_key": temp["event_key"],
                "match_number": temp["match_number"],
                "comp_level": temp["comp_level"],
                "set_number": temp["set_number"],
                "match_type": comp_levels[temp["comp_level"]],
                "winning_alliance": temp["winning_alliance"],
            }
            for alliance in temp["alliances"].keys():
                row[f"{alliance}_score"] = temp["alliances"][alliance]["score"]
                for i, team_key in enumerate(temp["alliances"][alliance]["team_keys"]):
                    row[f"{alliance}_team_{i + 1}"] = team_key
            data.append(row)
data = (
    pd.DataFrame(data)
    .sort_values(by=["event_key", "match_type", "match_number", "set_number"])
    .drop("match_type", axis=1)
)
data.to_sql("tba_matches", conn, if_exists="append", index=False)

conn.commit()
conn.close()
