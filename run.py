"""
run.py - Start the Scouting Hub web app.

USAGE
    python run.py

WHAT IT DOES
    1. Makes sure the database tables exist (db.init_db()).
    2. Starts the Flask web server so phones/iPads on the same router can open
       http://<laptop-ip-address>:5000

WHAT BELONGS HERE
    Only startup code. Keep it tiny. Features go in web/, ingest/, metrics/, etc.

TIP
    Find the laptop's address with `ipconfig` (Windows) or `ifconfig` / `ip addr`
    (Mac/Linux). Put it on a sticky note for the drive team.

LEVEL: Beginner.
"""

import config
import db
from web.app import create_app


def main() -> None:
    db.init_db()
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
