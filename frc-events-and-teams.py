from dotenv import load_dotenv, find_dotenv
import requests
import os
import base64
import pandas as pd
from tqdm import tqdm

start_year = 1992
end_year = 2025
# end_year = 2007


def frc_api_authorization(username: str, token: str):
    """Creates the FRC API authorization string"""
    encoded = base64.b64encode(f"{username}:{token}".encode("utf-8"))
    return encoded.decode("utf-8")


load_dotenv(find_dotenv())
authorization = frc_api_authorization(
    os.environ.get("FRC_USERNAME"), os.environ.get("FRC_TOKEN")
)

headers = {"Authorization": f"Basic {authorization}", "If-Modified-Since": ""}

teams = {}
data = []
events = []

for year in range(2006, end_year + 1):
    # print(year)
    url = f"https://frc-api.firstinspires.org/v3.0/{year}/events"

    response = requests.request("GET", url, headers=headers, data={})
    response = response.json()

    pbar = tqdm(response["Events"])
    for row in pbar:
        pbar.set_description(str(year))
        row["year"] = year
        events.append(row)

df = pd.DataFrame(events)
df.to_csv("frc-events.csv", index=False)

pbar = tqdm(range(start_year, end_year + 1))
for year in pbar:
    pbar.set_description(str(year))
    teams[year] = list()
    more_to_scrape = True
    page = 1
    while more_to_scrape:
        # print(f"{year} page {page}")
        url = f"https://frc-api.firstinspires.org/v3.0/{year}/teams?page={page}"
        response = requests.request("GET", url, headers=headers, data={})
        response = response.json()
        for team in response["teams"]:
            team_number = int(team["teamNumber"])
            teams[year].append(team_number)
            if team_number > 0:
                data.append({"year": year, "team": team_number})

        if response["pageCurrent"] == response["pageTotal"]:
            more_to_scrape = False
        else:
            page += 1

df = pd.DataFrame(data)
df.to_csv("fcr-teams.csv", index=False)
