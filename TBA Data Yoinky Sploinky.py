import requests
import json
import asyncio
import aiohttp
import time
from datetime import datetime

# Config
TBA_API_KEY = "your_api_key_here"
POWER_BI_MATCH_URL = "your_url_here"
POWER_BI_TEAM_URL = "your_url_here"

# Change this as necessary (ex. 2025nyro)
EVENT_KEY = "2025nyro"

HEADERS = {
    "X-TBA-Auth-Key": TBA_API_KEY,
    "Accept": "application/json"
}

LAST_MATCHES = {}
LAST_TEAM_STATS = {}

def log_message(message):
    """Prints timestamped log messages."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def clear_all_data():
    """Clears cached match and team stats data."""
    global LAST_MATCHES, LAST_TEAM_STATS
    LAST_MATCHES.clear()
    LAST_TEAM_STATS.clear()
    log_message("All stored match and team data has been cleared.")

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
                        await asyncio.sleep(5)
            except Exception as e:
                log_message(f"API Request Failed: {e}")
                await asyncio.sleep(5)
    return None

async def fetch_match_data():
    """Fetches match data and filters only new matches."""
    global LAST_MATCHES
    url = f"https://www.thebluealliance.com/api/v3/event/{EVENT_KEY}/matches/simple"
    matches = await fetch_data(url)

    if not matches:
        log_message("No match data received.")
        return []

    new_data = []
    for match in matches:
        match_key = f"{match['event_key']}_{match['match_number']}"
        scores = (match["alliances"]["red"]["score"], match["alliances"]["blue"]["score"])

        if match_key not in LAST_MATCHES or LAST_MATCHES[match_key] != scores:
            new_data.append({
                "event_key": match["event_key"],
                "match_number": match["match_number"],
                "blue_score": match["alliances"]["blue"]["score"],
                "red_score": match["alliances"]["red"]["score"]
            })
            LAST_MATCHES[match_key] = scores

    return new_data

async def fetch_team_stats():
    """Fetches OPR, DPR, and CCWM and filters only changed values."""
    global LAST_TEAM_STATS
    url = f"https://www.thebluealliance.com/api/v3/event/{EVENT_KEY}/oprs"
    data = await fetch_data(url)

    if not data or "oprs" not in data:
        log_message("No team performance data received.")
        return []

    new_data = []
    for team in data["oprs"]:
        opr, dpr, ccwm = data["oprs"][team], data["dprs"][team], data["ccwms"][team]
        stats = (opr, dpr, ccwm)

        if team not in LAST_TEAM_STATS or LAST_TEAM_STATS[team] != stats:
            new_data.append({
                "team_key": team,
                "event_key": EVENT_KEY,
                "opr": opr,
                "dpr": dpr,
                "ccwm": ccwm
            })
            LAST_TEAM_STATS[team] = stats

    return new_data

async def push_to_power_bi(url, data):
    """Pushes data to Power BI Streaming Dataset."""
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

async def update_data():
    """Main async loop that updates data repeatedly."""
    while True:
        try:
            match_data, team_data = await asyncio.gather(fetch_match_data(), fetch_team_stats())

            await asyncio.gather(
                push_to_power_bi(POWER_BI_MATCH_URL, match_data),
                push_to_power_bi(POWER_BI_TEAM_URL, team_data)
            )

            sleep_time = 20 if match_data or team_data else 60
            log_message(f"Sleeping for {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)

        except Exception as e:
            log_message(f"Unexpected error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    log_message(f"Power BI Live Data Sync Ready for Event: {EVENT_KEY}")
    while True:
        command = input("Enter command (start / clear / exit): ").strip().lower()
        if command == "start":
            asyncio.run(update_data())
        elif command == "clear":
            clear_all_data()
        elif command == "exit":
            log_message("Exiting script.")
            break
        else:
            log_message("Invalid command. Use 'start', 'clear', or 'exit'.")
