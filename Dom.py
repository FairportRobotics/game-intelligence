import os
import requests
import json



headers = {"X-TBA-Auth-Key": "uTHeEfPigDp9huQCpLNkWK7FBQIb01Qrzvt4MAjh9z2WQDkrsvNE77ch6bOPvPb6"}




def tba_matches(event_key: str):
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers
    )
    with open(f"data/matches_{event_key}.json", "wb") as f:
        f.write(response.content)
    return()





def tba_teams(event_key: str):
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams", headers
    )
    with open(f"data/teams_{event_key}.json", "wb") as f:
        f.write(response.content)
    return()



def tba_events(year: str):
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/events/{year}", headers
    )
    with open(f"data/events_{year}.json", "wb") as f:
        f.write(response.content)
    return()


key = "2025nyro"


year = "2025"


tba_matches(key)
tba_events(year)
tba_teams(key)
