"""
exports/db_sync.py - Copy the database to the standby laptop (or a USB drive).

USAGE
    python -m exports.db_sync                 # copy to config.BACKUP_DIR
    python -m exports.db_sync /media/usb      # copy to a USB drive

PURPOSE
    The standby laptop runs the same app with its own copy of the database. Run
    this every 30-60 minutes, after every scanning session, and after every pick
    list change during alliance selection.

WHAT SHOULD BE IN THIS FILE
    - backup_database(dest_dir): make a safe copy of the SQLite file with a
      timestamp in the name. Use the sqlite3 backup API (`conn.backup(other)`)
      instead of a plain file copy, so the copy is never half-written.
    - restore_database(backup_file): put a backup in place (used on the standby).
    - (Stretch) run on a schedule with APScheduler every
      config.DB_BACKUP_INTERVAL_MINUTES.

LEVEL: Advanced (but short!).
"""

import config  # noqa: F401


def backup_database(dest_dir: str | None = None) -> str:
    """TODO: copy the database safely. Return the path of the new backup file."""
    raise NotImplementedError


def restore_database(backup_file: str) -> None:
    """TODO: replace the current database with a backup file."""
    raise NotImplementedError
