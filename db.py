"""
db.py - Everything about talking to the SQLite database.

PURPOSE
    Every other file gets its database connection from here. If we ever move
    from SQLite to PostgreSQL, this is the file that changes.

WHAT BELONGS HERE
    - get_connection(): open the database file.
    - init_db(): create all tables from schema.sql (safe to run many times).
    - Small helper functions used in many places (query_all, query_one, execute).
    - data_freshness(): when was our data last updated, and from what source?
      (used by the "data last updated" banner on every web page).

WHAT DOES NOT BELONG HERE
    - Business logic (metrics, parsing, etc.). Those live in their own folders.

TIPS FOR STUDENTS
    - Always pass values to SQL with `?` placeholders, never by pasting them into
      the string. `execute("SELECT * FROM teams WHERE team_number = ?", (254,))`
      is safe. f-strings in SQL are how databases get broken.

LEVEL: Beginner to Intermediate.
"""

import sqlite3

import config


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

    TODO (Beginner): look at the `matches` and `rankings` tables and return
    something like {"as_of": "2026-03-14 14:14", "source": "tba"}.
    Return {"as_of": None, "source": None} if there is no data yet.
    """
    row = query_one("SELECT MAX(fetched_at) AS as_of FROM matches")
    return {"as_of": row["as_of"] if row else None, "source": None}
