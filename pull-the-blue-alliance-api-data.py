# This script pulls all match data from the blue alliance
# The data is saved in a CSV format that is similar to that found at
# https://github.com/the-blue-alliance/the-blue-alliance-data.


from dotenv import load_dotenv, find_dotenv
import os
import pandas as pd
import requests
from tqdm import tqdm

# Key settings
load_dotenv(find_dotenv())
headers = {"X-TBA-Auth-Key": os.environ.get("TBA_API_KEY")}
start_year = 2010
end_year = 2024
# Want to pull one year of data? Uncomment out the next line
# start_year = end_year = 2024


def tba_events(year: str):
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/events/{year}", headers
    )
    return response.json()


def tba_matches(event_key: str):
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers
    )
    return response.json()


for year in range(start_year, end_year + 1):
    # print(year)
    the_match_data = []
    pbar = tqdm(tba_events(year))
    for event in pbar:
        pbar.set_description(str(year))
        event_start_date = event["start_date"]
        event_end_date = event["end_date"]
        event_key = event["key"]
        for match in tba_matches(event_key):
            match_data = {
                "year": year,
                "event_key": event_key,
                "event_start_date": event_start_date,
                "event_end_date": event_end_date,
                "match_key": match["key"],
                "winning_alliance": match["winning_alliance"],
            }
            for color in ["red", "blue"]:
                teams = match["alliances"][color]["team_keys"]
                team_keys = [f"{color}{n}" for n in range(1, len(teams) + 1)]
                team_data = dict(zip(team_keys, teams))
                team_data[f"{color}_score"] = match["alliances"][color]["score"]
                match_data = {**match_data, **team_data}
            the_match_data.append(match_data)
    # Save the data as a csv if it exists
    if len(the_match_data) > 0:
        df = pd.DataFrame(the_match_data)
        df.to_csv(f"the-blue-alliance-api-data/{year}.csv", index=False)
