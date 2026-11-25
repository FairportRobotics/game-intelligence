from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IngestionSummary:
    created: int
    unchanged: int
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    replaced: int = 0


_canonical_records: dict[str, Any] = {}


def ingest_historic_event(normalized_batch: dict[str, Any]) -> IngestionSummary:
    season = normalized_batch["season"]
    event = normalized_batch["event"]
    teams = normalized_batch["teams"]
    matches = normalized_batch["matches"]

    candidate_records = [
        ("season", season["year"], season),
        ("event", event["key"], event),
    ]
    candidate_records.extend(
        ("team", team["number"], team) for team in teams
    )
    candidate_records.extend(
        ("match", match["key"], match) for match in matches
    )

    created = 0
    unchanged = 0
    updated = 0

    for record_type, key, value in candidate_records:
        identity = f"{record_type}:{key}"
        existing = _canonical_records.get(identity)
        if existing is None:
            _canonical_records[identity] = dict(value)
            created += 1
        elif existing == value:
            unchanged += 1
        else:
            _canonical_records[identity] = dict(value)
            updated += 1

    return IngestionSummary(
        created=created,
        unchanged=unchanged,
        updated=updated,
    )
