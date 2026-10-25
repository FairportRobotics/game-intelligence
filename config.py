"""
config.py - Settings for the whole project.

PURPOSE
    One place to read settings (event key, API keys, file paths, how often to
    poll). Every other file does `import config` instead of reading
    environment variables itself.

WHAT BELONGS HERE
    - Reading values from the `.env` file (secrets live there, NOT in code).
    - File paths (database, snapshots, backups).
    - Simple constants (poll interval, our team number).

WHAT DOES NOT BELONG HERE
    - Secrets typed directly into this file. Never commit an API key.
    - Logic. Keep this file boring.

LEVEL: Beginner. Good first file to read.
"""

import os
from pathlib import Path

# python-dotenv reads the ".env" file for us. If it is not installed (for
# example on a laptop set up offline), we fall back to normal environment vars.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "scouting.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
BACKUP_DIR = DATA_DIR / "backups"            # copies of the database (see exports/db_sync.py)
SNAPSHOT_DIR = DATA_DIR / "snapshots"        # self-contained HTML pages (see exports/snapshot.py)
PICKLIST_AUTOSAVE_DIR = DATA_DIR / "picklist_autosave"  # timestamped JSON pick list copies

# --- Event settings --------------------------------------------------------
EVENT_KEY = os.environ.get("EVENT_KEY", "2026nyro")   # TODO: change for each event
OUR_TEAM = int(os.environ.get("OUR_TEAM", "0"))        # TODO: our team number

# --- Secrets (come from .env) ----------------------------------------------
TBA_API_KEY = os.environ.get("TBA_API_KEY", "")
FIRST_API_USERNAME = os.environ.get("FIRST_API_USERNAME", "")
FIRST_API_TOKEN = os.environ.get("FIRST_API_TOKEN", "")
EVENT_PASSCODE = os.environ.get("EVENT_PASSCODE", "change-me")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-too")

# --- Timing ----------------------------------------------------------------
POLL_INTERVAL_SECONDS = 90        # how often ingest asks TBA for new data (be polite!)
PAGE_REFRESH_SECONDS = 30         # how often live pages refresh themselves (HTMX)
DB_BACKUP_INTERVAL_MINUTES = 30   # how often to copy the database to the standby

# --- Web server ------------------------------------------------------------
HOST = "0.0.0.0"   # 0.0.0.0 = reachable from phones/iPads on the same router
PORT = 5000
DEBUG = True       # TODO: set to False when running at an event
