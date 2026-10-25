"""
metrics/run_all.py - Run every metric calculation in one go.

USAGE
    python -m metrics.run_all

WHAT SHOULD BE IN THIS FILE
    - run(event_key=None): call, in order:
        opr.calculate(...), elo.calculate(...), trueskill_calc.calculate(...),
        scouted_averages.calculate(...)
      Each one saves its results into `team_metrics`.
    - Wrap each call in try/except so one broken metric does not stop the others
      (print which one failed and why).
    - Called automatically by ingest/poll_event.py after new matches arrive, and
      by the scan importer after new scouting data arrives.

LEVEL: Beginner (once the individual metrics exist).
"""

import config


def run(event_key: str | None = None) -> None:
    """TODO (Beginner): call each metric's calculate() function."""
    event_key = event_key or config.EVENT_KEY
    raise NotImplementedError("TODO: call each metric module")


if __name__ == "__main__":
    run()
