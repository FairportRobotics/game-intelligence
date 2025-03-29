import requests
import json
import asyncio
import aiohttp
import time
import os
from datetime import datetime

# Config
TBA_API_KEY = "your_api_key_here"
POWER_BI_MATCH_URL = "your_url_here"
POWER_BI_TEAM_URL = "your_url_here"
YEAR = "2025"  # Set the competition year

HEADERS = {
    "X-TBA-Auth-Key": TBA_API_KEY,
    "Accept": "application/json"
}

# Data Storage
LAST_MATCHES = {}
LAST_TEAM_STATS = {}

# Logging message function
def log_message(message):
    """Prints timestamped log messages."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# Clear all cached data
def clear_all_data():
    global LAST_MATCHES, LAST_TEAM_STATS
    LAST_MATCHES.clear()
    LAST_TEAM_STATS.clear()
    log_message("All stored match and team data has been cleared.")

# Async function to fetch data
async def fetch_data(url):
    """Fetch data from The Blue Alliance API with retry logic."""
    async with aiohttp.ClientSession() as session:
        for _ in range(3):  # Retry up to 3 times
            try:
                async with session.get(url, headers=HEADERS) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        log_message(f"Error {response.status}: Retrying...")
                        await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                log_message(f"API Request Failed: {e}")
                await asyncio.sleep(5)
    return None  # Return None if all retries fail

# Fetch all events for the specified year
async def fetch_all_events():
    """Fetches all FRC events in a given year."""
    url = f"https://www.thebluealliance.com/api/v3/events/{YEAR}/simple"
    events = await fetch_data(url)
    
    if not events:
        log_message("No events found for the specified year.")
        return []
    
    return [event["key"] for event in events]

# Fetch match data for all events
async def fetch_all_match_data(events):
    """Fetches match data for all events in the specified year."""
    global LAST_MATCHES
    new_data = []

    for event in events:
        url = f"https://www.thebluealliance.com/api/v3/event/{event}/matches/simple"
        matches = await fetch_data(url)

        if not matches:
            continue

        for match in matches:
            match_key = f"{match['event_key']}_{match['match_number']}"

            if match_key not in LAST_MATCHES or LAST_MATCHES[match_key] != (match["alliances"]["red"]["score"], match["alliances"]["blue"]["score"]):
                new_data.append({
                    "event_key": match["event_key"],
                    "match_number": match["match_number"],
                    "blue_score": match["alliances"]["blue"]["score"],
                    "red_score": match["alliances"]["red"]["score"]
                })
                LAST_MATCHES[match_key] = (match["alliances"]["red"]["score"], match["alliances"]["blue"]["score"])

    return new_data

# Fetch team statistics (OPR, DPR, CCWM) for all events
async def fetch_all_team_stats(events):
    """Fetches OPR, DPR, and CCWM for all events in the specified year."""
    global LAST_TEAM_STATS
    new_data = []

    for event in events:
        url = f"https://www.thebluealliance.com/api/v3/event/{event}/oprs"
        data = await fetch_data(url)

        if not data or "oprs" not in data:
            continue

        for team in data["oprs"]:
            team_key = team
            opr, dpr, ccwm = data["oprs"][team], data["dprs"][team], data["ccwms"][team]

            if team_key not in LAST_TEAM_STATS or LAST_TEAM_STATS[team_key] != (opr, dpr, ccwm):
                new_data.append({
                    "team_key": team_key,
                    "event_key": event,
                    "opr": opr,
                    "dpr": dpr,
                    "ccwm": ccwm
                })
                LAST_TEAM_STATS[team_key] = (opr, dpr, ccwm)

    return new_data

# Push data to Power BI
async def push_to_power_bi(url, data):
    """Pushes data to Power BI Streaming Dataset with error handling."""
    if not data:
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    log_message(f"{len(data)} records sent to Power BI.")
                else:
                    log_message(f"Power BI Push Failed: {response.status}, {await response.text()}")
        except Exception as e:
            log_message(f"Error sending data to Power BI: {e}")

# Main update function
async def update_data():
    """Fetches and pushes only new match & team data."""
    while True:
        try:
            events = await fetch_all_events()

            if not events:
                log_message("No events found. Retrying later...")
                await asyncio.sleep(60)
                continue

            match_data, team_data = await asyncio.gather(
                fetch_all_match_data(events),
                fetch_all_team_stats(events)
            )
            
            # Only fetches Team Data
            """
            team_data = await asyncio.gather(
                fetch_all_team_stats(events)
            )
            """

            await asyncio.gather(
                ## push_to_power_bi(POWER_BI_MATCH_URL, match_data),
                push_to_power_bi(POWER_BI_TEAM_URL, team_data)
            )

            sleep_time = 20 if match_data or team_data else 60
            log_message(f"Sleeping for {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)

        except Exception as e:
            log_message(f"Unexpected error: {e}")
            await asyncio.sleep(60)

# Run the script asynchronously
if __name__ == "__main__":
    log_message(f"Power BI Live Data Sync Started for Year: {YEAR}")
    
    while True:
        command = input("Enter command (start/clear/exit): ").strip().lower()
        
        if command == "start":
            asyncio.run(update_data())
        elif command == "clear":
            clear_all_data()
        elif command == "exit":
            log_message("Exiting program.")
            break
        else:
            log_message("Invalid command. Please enter 'start', 'clear', or 'exit'.")
