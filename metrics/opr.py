"""
metrics/opr.py - Offensive Power Rating, calculated from OUR match data.

PURPOSE
    TBA gives OPR when we are online. When we are not, we compute it ourselves
    from the matches we have (official, typed-in, or scouted).

THE IDEA
    Each alliance score = sum of the three teams' contributions. With many
    matches that is a system of equations: solve for the best contribution per
    team (least squares).
        A = a matrix with one row per alliance-in-a-match and one column per
            team; entry is 1 if the team was on that alliance, else 0.
        b = the alliance scores.
        Solve A x = b  ->  x[team] is that team's OPR.
    numpy.linalg.lstsq does the work. DPR/CCWM are variations of the same idea.

WHAT SHOULD BE IN THIS FILE
    - calculate(event_key): build A and b from the `matches` table (played matches
      only), solve, and save results to `team_metrics` as metric_name='opr'
      (and optionally 'dpr', 'ccwm') with source set to where the scores came from.

LEVEL: Intermediate (a good math/linear algebra project).
"""


def calculate(event_key: str) -> None:
    """TODO (Intermediate): compute OPR with least squares and save it."""
    raise NotImplementedError
