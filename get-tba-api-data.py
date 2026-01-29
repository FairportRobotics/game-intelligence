from dotenv import load_dotenv, find_dotenv
import os
import requests
from tqdm import tqdm

# Key settings
load_dotenv(find_dotenv())
headers = {"X-TBA-Auth-Key": os.environ.get("TBA_API_KEY")}
start_year = 1997  # 1997 is the earlies however match data begins in 2000
end_year = 2026
# start_year = end_year


def tba_events(year: str):
    """
    Pull the events for a given year from TBA

    :param year: The year to pull events for TBA
    :type year: str
    """
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/events/{year}", headers
    )
    return response.json()


def tba_matches(event_key: str):
    """
    Dull the matches for a given event from TBA

    :param event_key: The key for the event for TBA
    :type event_key: str
    """
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers
    )
    return response.json()


# Create directories to hold the data
for dir_path in ("./raw_data", "./raw_data/tba_events", "./raw_data/tba_matches"):
    os.makedirs(dir_path, exist_ok=True)

# Loop over the years requested
for year in range(start_year, end_year + 1):
    # Pull the event data
    events = tba_events(str(year))
    # Save it off
    with open(f"./raw_data/tba_events/{year}.json", "w") as f:
        f.write(str(events))
    # Loop over each event to get matches
    pbar = tqdm(events)
    for event in pbar:
        # Update the progress bar description
        pbar.set_description(str(year))
        # Get the matches for the event
        event_key = event["key"]
        matches = tba_matches(event_key)
        # Write the data if there is any
        if len(matches) > 0:
            with open(f"./raw_data/tba_matches/{event_key}.json", "w") as f:
                f.write(str(matches))
