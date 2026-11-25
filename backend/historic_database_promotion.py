"""Verify and atomically promote a historic Event database handoff."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "seasons": ("year", "data"),
    "teams": ("number", "data"),
    "events": ("key", "season_year", "data"),
    "event_teams": ("event_key", "team_number"),
    "matches": ("key", "event_key", "phase", "data", "provenance"),
    "match_alliance_teams": ("match_key", "alliance", "position", "team_number"),
}
_PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "seasons": ("year",),
    "teams": ("number",),
    "events": ("key",),
    "event_teams": ("event_key", "team_number"),
    "matches": ("key",),
    "match_alliance_teams": ("match_key", "alliance", "position"),
}
_REQUIRED_FOREIGN_KEYS = {
    ("events", "season_year", "seasons", "year"),
    ("event_teams", "event_key", "events", "key"),
    ("event_teams", "team_number", "teams", "number"),
    ("matches", "event_key", "events", "key"),
    ("match_alliance_teams", "match_key", "matches", "key"),
    ("match_alliance_teams", "team_number", "teams", "number"),
}


class CandidateDatabaseValidationError(ValueError):
    """A candidate is unreadable or does not satisfy the canonical database contract."""

    def __init__(self, issues: tuple[str, ...]) -> None:
        self.issues = issues
        super().__init__("Candidate database rejected: " + "; ".join(issues))


class DatabasePromotionError(RuntimeError):
    """A validated candidate could not be backed up or atomically promoted."""


@dataclass(frozen=True)
class PromotionResult:
    """The backup created before promotion, if a canonical database existed."""

    backup_path: Path | None


def _connect_readonly(database_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{database_path.as_uri()}?mode=ro", uri=True)


def _schema_issues(connection: sqlite3.Connection) -> list[str]:
    issues: list[str] = []
    present_tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }

    for table, required_columns in _REQUIRED_COLUMNS.items():
        if table not in present_tables:
            issues.append(f"required table {table!r} is missing")
            continue
        table_info = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
        columns = {row[1] for row in table_info}
        missing_columns = set(required_columns) - columns
        if missing_columns:
            issues.append(
                f"table {table!r} is missing columns "
                f"{', '.join(sorted(missing_columns))}"
            )
        primary_key = tuple(
            name
            for _, name in sorted(
                (row[5], row[1]) for row in table_info if row[5] > 0
            )
        )
        expected_key = _PRIMARY_KEYS[table]
        if primary_key != expected_key:
            issues.append(
                f"table {table!r} must have primary key "
                f"({', '.join(expected_key)})"
            )

    foreign_keys = {
        (table, row[3], row[2], row[4])
        for table in _REQUIRED_COLUMNS
        if table in present_tables
        for row in connection.execute(f'PRAGMA foreign_key_list("{table}")')
    }
    for child, column, parent, parent_column in sorted(
        _REQUIRED_FOREIGN_KEYS - foreign_keys
    ):
        issues.append(
            f"table {child!r}.{column} must reference "
            f"{parent!r}.{parent_column}"
        )

    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    for table, rowid, parent, _ in violations[:10]:
        issues.append(
            f"foreign-key violation in {table!r} row {rowid!r} "
            f"referencing {parent!r}"
        )
    if len(violations) > 10:
        issues.append(f"{len(violations) - 10} additional foreign-key violations")
    return issues


def _candidate_issues(database_path: Path) -> tuple[str, ...]:
    if not database_path.is_file():
        return (f"candidate file does not exist: {database_path}",)
    try:
        with closing(_connect_readonly(database_path)) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchall()
            issues = [
                f"SQLite integrity check failed: {result[0]}"
                for result in integrity
                if result[0] != "ok"
            ]
            issues.extend(_schema_issues(connection))
            return tuple(issues)
    except sqlite3.Error as error:
        return (f"candidate cannot be read as a SQLite database: {error}",)


def _copy_database(source_path: Path, destination_path: Path) -> None:
    with closing(_connect_readonly(source_path)) as source:
        with closing(sqlite3.connect(destination_path)) as destination:
            source.backup(destination)


def _backup_path(canonical_path: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    base = canonical_path.with_name(
        f"{canonical_path.stem}.backup-{timestamp}{canonical_path.suffix}"
    )
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = base.with_name(f"{base.stem}-{suffix}{base.suffix}")
        suffix += 1
    return candidate


def _preserve_canonical(canonical_path: Path) -> Path:
    backup_path = _backup_path(canonical_path)
    try:
        with closing(_connect_readonly(canonical_path)) as source:
            with closing(sqlite3.connect(backup_path)) as backup:
                source.backup(backup)
    except sqlite3.Error as error:
        backup_path.unlink(missing_ok=True)
        raise DatabasePromotionError(
            f"Could not back up canonical database {canonical_path}: {error}"
        ) from error
    return backup_path


def promote_historic_event_database(
    candidate_path: str | Path, canonical_path: str | Path
) -> PromotionResult:
    """Validate a candidate snapshot, back up canonical data, and atomically replace it.

    A previously returned backup can be passed as the next candidate to restore
    that database; candidate and canonical contents are never merged.
    """
    candidate = Path(candidate_path).expanduser().resolve()
    canonical = Path(canonical_path).expanduser().resolve()
    if candidate == canonical:
        raise CandidateDatabaseValidationError(
            ("candidate and canonical database paths must be different",)
        )
    issues = _candidate_issues(candidate)
    if issues:
        raise CandidateDatabaseValidationError(issues)
    if not canonical.parent.is_dir():
        raise DatabasePromotionError(
            f"Canonical database directory does not exist: {canonical.parent}"
        )

    descriptor, staging_name = tempfile.mkstemp(
        prefix=f".{canonical.name}.promotion-",
        suffix=".sqlite3",
        dir=canonical.parent,
    )
    os.close(descriptor)
    staging_path = Path(staging_name)
    try:
        try:
            _copy_database(candidate, staging_path)
        except sqlite3.Error as error:
            raise CandidateDatabaseValidationError(
                (f"candidate could not be snapshotted: {error}",)
            ) from error
        staged_issues = _candidate_issues(staging_path)
        if staged_issues:
            raise CandidateDatabaseValidationError(staged_issues)

        backup_path = (
            _preserve_canonical(canonical) if canonical.exists() else None
        )
        try:
            os.replace(staging_path, canonical)
        except OSError as error:
            raise DatabasePromotionError(
                f"Could not atomically promote candidate to {canonical}: {error}"
            ) from error
        return PromotionResult(backup_path=backup_path)
    finally:
        staging_path.unlink(missing_ok=True)
