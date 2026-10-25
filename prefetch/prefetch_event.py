"""
prefetch/prefetch_event.py - Download and save everything we need before the event.

USAGE
    python -m prefetch.prefetch_event            # uses EVENT_KEY from .env
    python -m prefetch.prefetch_event 2026nyro   # or name the event

WHAT IT SHOULD DO (in order)
    1. Save the event itself (name, dates)           -> events
    2. Save the team list for the event              -> teams, event_teams
    3. Save team history (past events, awards)       -> (add tables as needed)
    4. Save the match schedule IF it is posted yet   -> matches (source='tba')
    5. Call prefetch.statbotics_snapshot.run(event_key)  -> team_metrics
    6. Print a summary: "Saved 40 teams, 0 matches (schedule not posted), EPA for 38 teams"

RULES
    - Safe to run many times (use upserts, not plain INSERTs).
    - Set `fetched_at` on everything and `source` where the table has it.
    - If one step fails (no schedule yet, Statbotics down), print a clear message
      and CONTINUE with the other steps.

LEVEL: Intermediate.
"""

import sys

import config


def run(event_key: str) -> None:
    """TODO (Intermediate): implement steps 1-6 from the module docstring."""
    raise NotImplementedError("TODO: implement prefetch")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else config.EVENT_KEY)
