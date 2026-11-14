"""
db.py - Everything about talking to the SQLite database.

PURPOSE
    Every other file gets its database connection from here. If we ever move
    from SQLite to PostgreSQL, this is the file that changes.

WHAT BELONGS HERE
    - get_connection(): open the database file.
    - init_db(): create all tables from schema.sql (safe to run many times).
    - Migrate renamed TBA tables while preserving existing data.
    - Small helper functions used in many places (query_all, query_one, execute).
    - data_freshness(): when was our data last updated, and from what source?
      (used by the "data last updated" banner on every web page).

WHAT DOES NOT BELONG HERE
    - Business logic (metrics, parsing, etc.). Those live in their own folders.

TIPS FOR STUDENTS
    - Always pass values to SQL with `?` placeholders, never by pasting them into
      the string. `execute("SELECT * FROM tba_teams WHERE team_number = ?", (254,))`
      is safe. f-strings in SQL are how databases get broken.

LEVEL: Beginner to Intermediate.
"""

import json
import sqlite3
from datetime import datetime

import config

LEGACY_TBA_TABLES = (
    ("teams", "tba_teams"),
    ("events", "tba_events"),
    ("event_teams", "tba_event_teams"),
    ("matches", "tba_matches"),
    ("rankings", "tba_rankings"),
    ("raw_api_cache", "raw_tba_api_data"),
)


def get_connection() -> sqlite3.Connection:
    """Open the database. Rows come back like dicts: row["team_number"]."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create all tables from schema.sql. Safe to run repeatedly (uses IF NOT EXISTS)."""
    with get_connection() as conn:
        existing_tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        for old_name, new_name in LEGACY_TBA_TABLES:
            if old_name in existing_tables and new_name not in existing_tables:
                conn.execute(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"')
                existing_tables.remove(old_name)
                existing_tables.add(new_name)
        conn.executescript(config.SCHEMA_PATH.read_text())


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Run a SELECT and return every row."""
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()):
    """Run a SELECT and return the first row (or None)."""
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql: str, params: tuple = ()) -> None:
    """Run an INSERT/UPDATE/DELETE and save it."""
    with get_connection() as conn:
        conn.execute(sql, params)


def data_freshness() -> dict:
    """
    Return the newest `fetched_at` and its `source` for the freshness banner.

    TODO (Beginner): look at the `tba_matches` and `tba_rankings` tables and return
    something like {"as_of": "2026-03-14 14:14", "source": "tba"}.
    Return {"as_of": None, "source": None} if there is no data yet.
    """
    row = query_one("SELECT MAX(fetched_at) AS as_of FROM tba_matches")
    if row:
        return {"as_of": row["as_of"], "source": "tba"}
    return {"as_of": None, "source": None}


def get_etag(path: str) -> str | None:
    """Return the cached ETag for an API path, or None if it has not been cached."""
    row = query_one("SELECT etag FROM raw_tba_api_data WHERE url = ?", (path,))
    return row["etag"] if row else None


def get_cached_response(path: str) -> dict | None:
    """Return the cached response for an API path, or None if it has not been cached."""
    row = query_one("SELECT response_json FROM raw_tba_api_data WHERE url = ?", (path,))
    return json.loads(row["response_json"]) if row else None


def get_fetched_at() -> int:
    """Return the timestamp in a YYYYMMDD.HHMMSS format."""
    return int(datetime.now().strftime("%Y%m%d.%H%M%S"))
