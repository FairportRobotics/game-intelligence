"""
ingest/tba_client.py - A small helper for calling The Blue Alliance API v3.

PURPOSE
    One function that fetches a TBA URL politely and safely. Everything that
    needs TBA data (prefetch/ and ingest/) uses this instead of calling
    `requests` directly.

WHAT SHOULD BE IN THIS FILE
    - get(path): fetch https://www.thebluealliance.com/api/v3<path>
        * send the header X-TBA-Auth-Key (from config.TBA_API_KEY)
        * send If-None-Match with the saved ETag (from raw_api_cache)
        * on 304 Not Modified: return the cached response (cheap!)
        * on 200: save the new response + ETag to raw_api_cache, return it
        * on ANY network error: return the cached response if we have one,
          otherwise return None. NEVER raise an error that crashes the app.
    - Convenience wrappers: get_event_teams(event_key), get_event_matches(event_key),
      get_event_rankings(event_key), get_event_oprs(event_key), get_team(team_number)

TBA docs: https://www.thebluealliance.com/apidocs/v3

ETIQUETTE
    Do not poll faster than once a minute or two. Never print or commit the API key.

LEVEL: Intermediate.
"""

import config  # noqa: F401  (used once you implement get())

TBA_BASE_URL = "https://www.thebluealliance.com/api/v3"


def get(path: str):
    """
    Fetch one TBA endpoint (for example "/event/2026nyro/teams") and return the
    parsed JSON, or None if we have nothing.

    TODO (Intermediate):
      1. Look up the saved ETag for this URL in the raw_api_cache table.
      2. Call requests.get(...) with the auth header and If-None-Match header,
         with a short timeout (like 10 seconds).
      3. Handle 304 / 200 / errors as described in the module docstring.
    """
    raise NotImplementedError("TODO: implement the TBA fetch with ETag caching")


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
