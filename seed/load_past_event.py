"""
seed/load_past_event.py - Load a PAST event so we can develop with real-looking data.

USAGE
    python seed/load_past_event.py                # loads the default sample event
    python seed/load_past_event.py 2025nyro       # or a specific past event key

WHY
    New students should see a working site within 10 minutes of cloning the repo,
    without waiting for a live event.

WHAT SHOULD BE IN THIS FILE
    - Initialize the database (db.init_db()).
    - Load a past event's teams and matches into the database. Easiest path:
        a) Use prefetch/ and ingest/tba_client.py to download last season's event, OR
        b) Save the JSON responses once into seed/sample_data/ and load them from
           those files, so seeding works with NO internet.
    - (Stretch) Generate fake scouting rows in `match_scouting` so the metrics and
      pages have something to show.

LEVEL: Beginner to Intermediate.
"""

import db


def main() -> None:
    db.init_db()
    # TODO (Intermediate): load teams, matches, and rankings for a past event.
    print("Database initialized. TODO: load sample event data.")


if __name__ == "__main__":
    main()
