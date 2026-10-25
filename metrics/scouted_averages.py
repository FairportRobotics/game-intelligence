"""
metrics/scouted_averages.py - Summarize OUR scouting data per team.

PURPOSE
    Turn rows in `match_scouting` (one per robot per match) into one number per
    team per field, for example average cycles or climb success rate.

WHAT SHOULD BE IN THIS FILE
    - calculate(event_key):
        1. Read `field_definitions` to learn which fields are numbers/booleans
           and how to aggregate each (avg, pct, max, sum).
        2. Load `match_scouting`, unpack the JSON `data` column (pandas works well).
        3. Group by team_number and aggregate each field.
        4. Save to `team_metrics` as metric_name='scouted_<field>' (source='scouted').
    - Reliability: percentage of matches where the robot broke down or did not move
      (once the config has a field for that).
    - (Advanced stretch) Normalize subjective ratings per scout so a harsh scout
      and a generous scout are comparable.

BECAUSE THIS READS field_definitions, IT SHOULD KEEP WORKING WHEN THE GAME CHANGES.

LEVEL: Intermediate (averages) / Advanced (scout-bias normalization).
"""


def calculate(event_key: str) -> None:
    """TODO (Intermediate): compute and save scouted averages for every team."""
    raise NotImplementedError
