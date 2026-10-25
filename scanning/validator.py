"""
scanning/validator.py - Check a parsed scan before we save it.

PURPOSE
    Catch scouting mistakes while the scout is still nearby to fix them.

WHAT SHOULD BE IN THIS FILE
    - validate(record): raise ValueError("short reason") if anything is wrong.
      Checks to include:
        1. Required fields are present and the right type.
        2. The event_key matches the event we are at (config.EVENT_KEY).
        3. The team is actually IN that match, according to the `matches` table
           (this catches mistyped team numbers).
        4. The match exists in the schedule. (If the schedule is not loaded yet,
           return a warning instead of an error so scanning is not blocked.)
    - check_totals(event_key, match_key): compare the sum of scouted points for
      an alliance to the official score. Return a list of problems. This runs as
      a separate job AFTER a match (not during a scan); results feed the
      "Data quality" page.

LEVEL: Intermediate (checks 1-4) / Advanced (check_totals).
"""


def validate(record: dict) -> None:
    """TODO (Intermediate): raise ValueError with a clear reason if the record is bad."""
    raise NotImplementedError


def check_totals(event_key: str, match_key: str) -> list[str]:
    """TODO (Advanced): compare scouted totals to the official alliance scores."""
    raise NotImplementedError
