"""
scanning/importer.py - Save scans in the database. Used by the Scan page.

PURPOSE
    The one function the web app calls for every scan:
        status = import_scan(raw_text)   # -> "saved", "updated", or raises ValueError

WHAT IMPORT_SCAN SHOULD DO (in this order)
    1. Save raw_text to `raw_scans` FIRST, no matter what. (If our parser has a
       bug, we can replay every scan later without anyone rescanning.)
    2. parser.parse_scan(raw_text)
    3. validator.validate(record)
    4. UPSERT into `match_scouting` or `pit_scouting`:
         - match key = (event_key, match_key, team_number)
         - pit key   = (event_key, team_number)
         - store game-specific answers as JSON in the `data` column
       Scanning the same code twice must UPDATE the row, not duplicate it.
       (SQLite: INSERT ... ON CONFLICT(...) DO UPDATE SET ...)
    5. Update the `raw_scans` row with status and error_message.
    6. Return a short status string for the Scan page ("Match 12, Team 254 saved").

ALSO USEFUL
    - reprocess_raw_scans(): re-run every row in `raw_scans` through the current
      parser (after fixing a parser bug).
    - import_csv(path): load a ScoutingPASS CSV export (fallback if QR scanning fails).

LEVEL: Intermediate to Advanced.
"""


def import_scan(raw_text: str) -> str:
    """TODO (Intermediate): implement steps 1-6 from the module docstring."""
    raise NotImplementedError


def reprocess_raw_scans() -> int:
    """TODO (Advanced): re-parse every saved raw scan. Return how many were saved."""
    raise NotImplementedError


def import_csv(path: str) -> int:
    """TODO (Beginner/Intermediate): import a CSV export. Return the number of rows saved."""
    raise NotImplementedError
