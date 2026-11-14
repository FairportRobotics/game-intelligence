"""
ingest/tba_client.py - A small helper for calling The Blue Alliance API v3.

PURPOSE
    One function that fetches a TBA URL politely and safely. Everything that
    needs TBA data (prefetch/ and ingest/) uses this instead of calling
    `requests` directly.

WHAT SHOULD BE IN THIS FILE
    - get(path): fetch https://www.thebluealliance.com/api/v3<path>
        * send the header X-TBA-Auth-Key (from config.TBA_API_KEY)
        * send If-None-Match with the saved ETag (from raw_tba_api_data)
        * on 304 Not Modified: return the cached response (cheap!)
        * on 200: save the new response + ETag to raw_tba_api_data, return it
        * on ANY network error: return the cached response if we have one,
          otherwise return None. NEVER raise an error that crashes the app.
    - Convenience wrappers: get_event_teams(event_key), get_event_matches(event_key),
      get_event_rankings(event_key), get_event_oprs(event_key), get_team(team_number)

TBA docs: https://www.thebluealliance.com/apidocs/v3

ETIQUETTE
    Do not poll faster than once a minute or two. Never print or commit the API key.

LEVEL: Intermediate.
"""

import config
import db
import requests

TBA_BASE_URL = "https://www.thebluealliance.com/api/v3"


def get(path: str) -> dict | None:
    """
    Fetch one TBA endpoint (for example "/event/2026nyro/teams") and return the
    parsed JSON, or None if we have nothing.
    """

    # 1. Look up the saved ETag for this URL in raw_tba_api_data.
    saved_etag = db.get_etag(path)

    # 2. Call requests.get(...) with the auth header and If-None-Match header, with a short timeout (like 10 seconds).
    headers = {"X-TBA-Auth-Key": config.TBA_API_KEY}
    if saved_etag:
        headers["If-None-Match"] = saved_etag
    try:
        response = requests.get(f"{TBA_BASE_URL}{path}", headers=headers, timeout=10)

    # 3. Handle 304 / 200 / errors as described in the module docstring.
    except requests.RequestException:
        return db.get_cached_response(path)

    if response.status_code == 304:
        return db.get_cached_response(path)

    if response.status_code == 200:
        # Save the new response and ETag to the cache.
        fetched_at = db.get_fetched_at()
        db.execute(
            "INSERT INTO raw_tba_api_data (url, response_json, etag, fetched_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(url) DO UPDATE SET response_json = ?, etag = ?, fetched_at = ?",
            (
                path,
                response.text,
                response.headers.get("ETag"),
                fetched_at,
                response.text,
                response.headers.get("ETag"),
                fetched_at,
            ),
        )
        # Return the freshly fetched data.
        return response.json()


def get_event_teams(event_key: str):
    """Return the list of teams at an event. TODO: call get(f'/event/{event_key}/teams')."""
    raise NotImplementedError


def get_event_matches(event_key: str):
    """Return every match (scheduled and played) for an event."""
    raise NotImplementedError


def get_event_rankings(event_key: str):
    """Return the current qualification rankings for an event."""
    raise NotImplementedError


def get_event_oprs(event_key: str):
    """Return OPR / DPR / CCWM for every team at an event."""
    raise NotImplementedError
