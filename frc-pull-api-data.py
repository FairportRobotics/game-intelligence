from dotenv import load_dotenv, find_dotenv
import requests
import os
import base64
import pandas as pd
from tqdm import tqdm

start_year = 2024  # 1992
end_year = 2024
# end_year = start_year = 2009

problem_events = set()


def frc_api_authorization(username: str, token: str):
    """Creates the FRC API authorization string"""
    encoded = base64.b64encode(f"{username}:{token}".encode("utf-8"))
    return encoded.decode("utf-8")


load_dotenv(find_dotenv())
authorization = frc_api_authorization(
    os.environ.get("FRC_USERNAME"), os.environ.get("FRC_TOKEN")
)

payload = {}
headers = {"Authorization": f"Basic {authorization}", "If-Modified-Since": ""}

for year in range(start_year, end_year + 1):
    the_match_data = []
    response = requests.request(
        "GET",
        f"https://frc-api.firstinspires.org/v3.0/{year}/events",
        headers=headers,
        data=payload,
    )

    response = response.json()
    events = response["Events"]
    pbar = tqdm(events)
    for event in pbar:
        pbar.set_description(str(year))
        event_code = event["code"]
        url = f"https://frc-api.firstinspires.org/v3.0/{year}/matches/{event_code}"
        response = requests.request("GET", url, headers=headers, data=payload)
        try:
            response = response.json()
            matches = response["Matches"]
            for match in matches:
                teams = match["teams"].copy()
                match.pop("teams")
                for team in teams:
                    match[team["station"]] = team["teamNumber"]
                    match[team["station"] + "_dq"] = team["dq"]
                match["event_code"] = event_code
                the_match_data.append(match)
        except:
            problem_events.add(url)
            continue

    if len(the_match_data) > 0:
        df = pd.DataFrame(the_match_data)
        df.to_csv(f"frc-api-data/{year}.csv", index=False)

if len(problem_events) > 0:
    with open("frc-api-failures.txt", "w") as f:
        for problem_event in problem_events:
            f.write(f"{problem_event}\n")
