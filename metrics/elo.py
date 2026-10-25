"""
metrics/elo.py - Elo ratings for teams.

THE IDEA
    1. Every team starts at a rating (default 1500). Better: seed from last
       season's rating (metric 'epa_prev_season' from the Statbotics snapshot).
    2. For each played match in time order:
         - alliance rating = average (or sum) of its three teams' ratings
         - expected win chance for red = 1 / (1 + 10 ** ((blue - red) / 400))
         - actual result: 1 if red won, 0 if blue won, 0.5 for a tie
         - each team's rating moves by K * (actual - expected); K is ~20-32
    3. Save the final rating per team.

WHAT SHOULD BE IN THIS FILE
    - expected_score(rating_a, rating_b): the formula above.
    - update_ratings(...): apply one match's result.
    - calculate(event_key): load matches, run the loop, save to `team_metrics`
      as metric_name='elo'.
    - (Stretch) Save the rating after every match so we can draw trend charts.

TESTS
    tests/test_elo.py checks expected_score() with simple cases.

LEVEL: Intermediate (a great first metrics project).
"""

DEFAULT_RATING = 1500
K_FACTOR = 24


def expected_score(rating_a: float, rating_b: float) -> float:
    """
    Chance (0 to 1) that a side rated `rating_a` beats a side rated `rating_b`.

    TODO (Beginner): implement the formula from the module docstring.
    """
    raise NotImplementedError


def calculate(event_key: str) -> None:
    """TODO (Intermediate): run through all played matches and save 'elo' per team."""
    raise NotImplementedError
