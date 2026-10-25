"""
metrics/trueskill_calc.py - TrueSkill ratings for teams.

(The file is not named trueskill.py so it does not clash with the package.)

THE IDEA
    TrueSkill gives each team a skill estimate (mu) AND an uncertainty (sigma).
    It handles 3-team alliances naturally. The `trueskill` package does the math:

        import trueskill
        env = trueskill.TrueSkill(draw_probability=0.0)
        ratings = {team: env.create_rating() for team in teams}
        # for each match: rate([red_ratings, blue_ratings], ranks=[0, 1])
        #                 ranks: lower number = better (0 = winner)

WHAT SHOULD BE IN THIS FILE
    - calculate(event_key): process played matches in time order, then save per
      team: 'trueskill' (use a conservative score like mu - 3*sigma) and
      optionally 'trueskill_mu' and 'trueskill_sigma'.

LEVEL: Intermediate.
"""


def calculate(event_key: str) -> None:
    """TODO (Intermediate): use the trueskill package to rate every team and save results."""
    raise NotImplementedError
