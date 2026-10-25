"""
ingest/first_client.py - A helper for the official FIRST FRC Events API.

PURPOSE
    A SECOND live source in case TBA is slow or down on a busy competition day.
    It should give the same kind of data as tba_client.py so poll_event.py can
    switch between them.

WHAT SHOULD BE IN THIS FILE
    - get(path): call https://frc-api.firstinspires.org/v3.0/<season><path> with
      HTTP Basic auth (config.FIRST_API_USERNAME / config.FIRST_API_TOKEN).
    - Functions that return teams, schedule, scores, and rankings.
    - A "translate" step that converts FIRST's field names into the same
      dictionaries tba_client returns (so the rest of our code does not care
      which source was used).

STATUS: Phase 3 / stretch. Skip until the TBA path works end to end.

LEVEL: Advanced.
"""

FIRST_BASE_URL = "https://frc-api.firstinspires.org/v3.0"


def get(path: str):
    """TODO (Advanced): fetch from the FIRST API with basic auth and error handling."""
    raise NotImplementedError("TODO: implement the FIRST API client")
