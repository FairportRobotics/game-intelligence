from dotenv import load_dotenv, find_dotenv
import os
import requests
from tqdm import tqdm

for dir_path in ("./raw_data", "./raw_data/tba_events", "./raw_data/tba_matches"):
    os.makedirs(dir_path, exist_ok=True)

# Key settings
load_dotenv(find_dotenv())
headers = {"X-TBA-Auth-Key": os.environ.get("TBA_API_KEY")}
start_year = 1997       
end_year = 2026
#start_year = end_year = 2000

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
    events = tba_events(year)
    with open(f"./raw_data/tba_events/{year}.json", "w") as f:
        f.write(str(events))

    pbar = tqdm(events)
    for event in pbar:
        pbar.set_description(str(year))
        event_key = event["key"]
        matches = tba_matches(event_key)
        if len(matches) > 0:
            with open(f"./raw_data/tba_matches/{event_key}.json", "w") as f:
                f.write(str(matches))

    #print(events)