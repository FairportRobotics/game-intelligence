"""
prefetch/statbotics_snapshot.py - Save a snapshot of Statbotics EPA ratings.

PURPOSE
    Statbotics will probably be unreachable at the venue, so we save its numbers
    BEFORE the event with a timestamp.

WHAT IT SHOULD DO
    - Use the `statbotics` Python package (or its REST API) to get, for every team
      at the event: this season's EPA, last season's EPA, and the team's history.
    - Save them into `team_metrics` as:
          metric_name='epa_pre_event', source='statbotics', updated_at=now
      (Also save last season's rating under a separate name such as 'epa_prev_season'.
       metrics/elo.py uses it to seed starting ratings.)
    - Only update `epa_live` when the web app/ingest is online during the event.

RULES
    - ONLY this file (and ingest/) may talk to Statbotics. The web app never does.
    - If Statbotics is down, print a message and return. Do not crash prefetch.

LEVEL: Intermediate.
"""


def run(event_key: str) -> None:
    """TODO (Intermediate): fetch EPA for each team at the event and save it."""
    raise NotImplementedError("TODO: implement the Statbotics snapshot")
