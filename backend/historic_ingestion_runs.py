"""Resume and report selected historic Event ingestion work."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.historic_ingestion import (
    IngestionSummary,
    NormalizedHistoricBatch,
)


@dataclass(frozen=True)
class EventSource:
    event_key: str
    source: str


@dataclass(frozen=True)
class SourceResult:
    batch: NormalizedHistoricBatch | None = None
    unchanged: bool = False
    skipped: bool = False


class TransientSourceError(Exception):
    """A source adapter reports an error that may succeed on a later attempt."""


class SourceAdapter(Protocol):
    def fetch_event(self, event_key: str, source: str) -> SourceResult: ...


class EventIngestor(Protocol):
    def __call__(
        self,
        normalized_batch: NormalizedHistoricBatch,
        *,
        database_path: str | Path,
    ) -> IngestionSummary: ...


@dataclass(frozen=True)
class FailureDetail:
    event_key: str
    source: str
    attempts: int
    reason: str


@dataclass(frozen=True)
class RunSummary:
    created: int
    updated: int
    unchanged: int
    skipped: int
    failed: int
    replaced: int
    completed_events: tuple[str, ...]
    skipped_events: tuple[str, ...]
    failed_events: tuple[str, ...]
    ingestion_summary: IngestionSummary
    human_summary: str
    failure_details: tuple[FailureDetail, ...]


_COUNT_FIELDS = ("created", "updated", "unchanged", "skipped", "failed", "replaced")


def _initialize_checkpoints(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS ingestion_runs (
            run_id TEXT PRIMARY KEY,
            manifest TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ingestion_checkpoints (
            run_id TEXT NOT NULL REFERENCES ingestion_runs(run_id),
            event_key TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            counts TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            PRIMARY KEY (run_id, event_key, source)
        );
        """
    )


def _count_record(summary: IngestionSummary) -> dict[str, int]:
    return {field: getattr(summary, field) for field in _COUNT_FIELDS}


def _empty_counts() -> dict[str, int]:
    return dict.fromkeys(_COUNT_FIELDS, 0)


def _human_summary(
    completed: tuple[str, ...],
    skipped: tuple[str, ...],
    failed: tuple[str, ...],
) -> str:
    def listed(events: tuple[str, ...]) -> str:
        return ", ".join(events) if events else "none"

    return (
        f"Completed: {listed(completed)}. "
        f"Skipped: {listed(skipped)}. Failed: {listed(failed)}."
    )


def run_historic_ingestion(
    *,
    run_id: str,
    event_sources: list[EventSource],
    source_adapter: SourceAdapter,
    ingest_event: EventIngestor,
    canonical_database_path: str | Path,
    checkpoint_database_path: str | Path,
    max_attempts: int = 3,
) -> RunSummary:
    """Fetch and ingest selected Events, persisting progress for later resumption."""
    manifest_items = [(item.event_key, item.source) for item in event_sources]
    if not run_id or any(not event or not source for event, source in manifest_items):
        raise ValueError("run_id, Event keys, and sources must be non-empty")
    if len(set(manifest_items)) != len(manifest_items):
        raise ValueError("event_sources must not contain duplicate Event/source pairs")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")

    manifest = json.dumps(manifest_items, separators=(",", ":"))
    connection = sqlite3.connect(checkpoint_database_path)
    try:
        _initialize_checkpoints(connection)
        with connection:
            row = connection.execute(
                "SELECT manifest FROM ingestion_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if row is not None and row[0] != manifest:
                raise ValueError(
                    "run_id is already associated with a different selection"
                )
            connection.execute(
                "INSERT OR IGNORE INTO ingestion_runs (run_id, manifest) VALUES (?, ?)",
                (run_id, manifest),
            )
            for event_key, source in manifest_items:
                connection.execute(
                    "INSERT OR IGNORE INTO ingestion_checkpoints "
                    "(run_id, event_key, source, status, counts) "
                    "VALUES (?, ?, ?, 'pending', ?)",
                    (run_id, event_key, source, json.dumps(_empty_counts())),
                )

        for event_key, source in manifest_items:
            with connection:
                checkpoint = connection.execute(
                    "SELECT status FROM ingestion_checkpoints "
                    "WHERE run_id = ? AND event_key = ? AND source = ?",
                    (run_id, event_key, source),
                ).fetchone()
                if checkpoint[0] in {"completed", "unchanged", "skipped"}:
                    continue
                connection.execute(
                    "UPDATE ingestion_checkpoints SET status = 'running', error = NULL "
                    "WHERE run_id = ? AND event_key = ? AND source = ?",
                    (run_id, event_key, source),
                )

            status = "failed"
            counts = _empty_counts()
            counts["failed"] = 1
            error = "Source failure"
            for attempt in range(1, max_attempts + 1):
                with connection:
                    connection.execute(
                        "UPDATE ingestion_checkpoints SET attempts = attempts + 1 "
                        "WHERE run_id = ? AND event_key = ? AND source = ?",
                        (run_id, event_key, source),
                    )
                try:
                    result = source_adapter.fetch_event(event_key, source)
                except TransientSourceError:
                    error = (
                        f"Transient source failure after attempt {attempt}; "
                        "verify source availability and retry the run."
                    )
                    if attempt < max_attempts:
                        continue
                    break
                except Exception as exception:
                    error = (
                        f"Non-retryable source failure ({type(exception).__name__}); "
                        "check the adapter configuration and selected Event/source."
                    )
                    break

                if result.unchanged:
                    status = "unchanged"
                    counts = _empty_counts()
                    counts["unchanged"] = 1
                elif result.skipped:
                    status = "skipped"
                    counts = _empty_counts()
                    counts["skipped"] = 1
                elif result.batch is None:
                    error = (
                        "Source returned neither a batch nor a status; "
                        "fix the adapter response before retrying."
                    )
                    break
                else:
                    try:
                        ingestion = ingest_event(
                            result.batch, database_path=canonical_database_path
                        )
                    except Exception as exception:
                        error = (
                            f"Ingestion failed ({type(exception).__name__}); "
                            "correct the normalized batch before resuming."
                        )
                        break
                    status = "completed"
                    counts = _count_record(ingestion)
                error = None
                break

            with connection:
                connection.execute(
                    "UPDATE ingestion_checkpoints "
                    "SET status = ?, counts = ?, error = ? "
                    "WHERE run_id = ? AND event_key = ? AND source = ?",
                    (
                        status,
                        json.dumps(counts, separators=(",", ":")),
                        error,
                        run_id,
                        event_key,
                        source,
                    ),
                )

        totals = _empty_counts()
        completed: list[str] = []
        skipped: list[str] = []
        failed: list[str] = []
        failure_details: list[FailureDetail] = []
        for event_key, source in manifest_items:
            checkpoint = connection.execute(
                "SELECT status, counts, attempts, error FROM ingestion_checkpoints "
                "WHERE run_id = ? AND event_key = ? AND source = ?",
                (run_id, event_key, source),
            ).fetchone()
            status, counts_data, attempts, error = checkpoint
            counts = json.loads(counts_data)
            for field in _COUNT_FIELDS:
                totals[field] += counts[field]
            if status == "completed":
                completed.append(event_key)
            elif status in {"unchanged", "skipped"}:
                skipped.append(event_key)
            elif status == "failed":
                failed.append(event_key)
                failure_details.append(
                    FailureDetail(
                        event_key=event_key,
                        source=source,
                        attempts=attempts,
                        reason=error or "Ingestion failed without a recorded reason",
                    )
                )

        unique_completed = tuple(dict.fromkeys(completed))
        unique_skipped = tuple(dict.fromkeys(skipped))
        unique_failed = tuple(dict.fromkeys(failed))
        ingestion_summary = IngestionSummary(
            created=totals["created"],
            updated=totals["updated"],
            unchanged=totals["unchanged"],
            skipped=totals["skipped"],
            failed=totals["failed"],
            replaced=totals["replaced"],
        )
        return RunSummary(
            **totals,
            completed_events=unique_completed,
            skipped_events=unique_skipped,
            failed_events=unique_failed,
            ingestion_summary=ingestion_summary,
            human_summary=_human_summary(
                unique_completed, unique_skipped, unique_failed
            ),
            failure_details=tuple(failure_details),
        )
    finally:
        connection.close()
