import sqlite3
from pathlib import Path

import pytest

from backend.historic_database_promotion import (
    CandidateDatabaseValidationError,
    promote_historic_event_database,
)
from backend.historic_ingestion import (
    NormalizedHistoricBatch,
    ingest_historic_event,
)


def _batch(year: int, event_key: str, first_team: int) -> NormalizedHistoricBatch:
    second_team = first_team + 1
    return {
        "season": {"year": year},
        "event": {"key": event_key, "name": f"Event {year}"},
        "teams": [
            {"number": first_team, "name": f"Team {first_team}"},
            {"number": second_team, "name": f"Team {second_team}"},
        ],
        "matches": [
            {
                "key": f"{event_key}_qm1",
                "type": "qualification",
                "number": 1,
                "red": [first_team],
                "blue": [second_team],
            }
        ],
        "source": "tba",
    }


def test_promotion_replaces_canonical_database_and_backup_can_restore_it(
    tmp_path: Path,
) -> None:
    canonical = tmp_path / "canonical.sqlite3"
    candidate = tmp_path / "candidate.sqlite3"
    previous_batch = _batch(2023, "2023nyro", 100)
    candidate_batch = _batch(2024, "2024nyro", 200)

    ingest_historic_event(previous_batch, database_path=canonical)
    ingest_historic_event(candidate_batch, database_path=candidate)

    promotion = promote_historic_event_database(candidate, canonical)

    assert promotion.backup_path is not None
    assert promotion.backup_path.is_file()
    assert ingest_historic_event(
        candidate_batch, database_path=canonical
    ).unchanged == 5
    assert ingest_historic_event(previous_batch, database_path=canonical).created == 5
    assert ingest_historic_event(
        previous_batch, database_path=promotion.backup_path
    ).unchanged == 5

    promote_historic_event_database(promotion.backup_path, canonical)
    assert ingest_historic_event(previous_batch, database_path=canonical).unchanged == 5
    assert ingest_historic_event(candidate_batch, database_path=canonical).created == 5


def test_incomplete_candidate_is_rejected_without_changing_canonical(
    tmp_path: Path,
) -> None:
    canonical = tmp_path / "canonical.sqlite3"
    candidate = tmp_path / "candidate.sqlite3"
    previous_batch = _batch(2023, "2023nyro", 100)
    candidate_batch = _batch(2024, "2024nyro", 200)

    ingest_historic_event(previous_batch, database_path=canonical)
    ingest_historic_event(candidate_batch, database_path=candidate)
    with sqlite3.connect(candidate) as connection:
        connection.execute("DROP TABLE match_alliance_teams")

    with pytest.raises(
        CandidateDatabaseValidationError, match="required table 'match_alliance_teams'"
    ):
        promote_historic_event_database(candidate, canonical)

    assert ingest_historic_event(previous_batch, database_path=canonical).unchanged == 5
    assert ingest_historic_event(candidate_batch, database_path=canonical).created == 5


def test_candidate_with_broken_team_relationship_is_rejected(
    tmp_path: Path,
) -> None:
    canonical = tmp_path / "canonical.sqlite3"
    candidate = tmp_path / "candidate.sqlite3"
    previous_batch = _batch(2023, "2023nyro", 100)
    candidate_batch = _batch(2024, "2024nyro", 200)

    ingest_historic_event(previous_batch, database_path=canonical)
    ingest_historic_event(candidate_batch, database_path=candidate)
    with sqlite3.connect(candidate) as connection:
        connection.execute("DELETE FROM teams WHERE number = 200")

    with pytest.raises(
        CandidateDatabaseValidationError, match="foreign-key violation"
    ):
        promote_historic_event_database(candidate, canonical)

    assert ingest_historic_event(previous_batch, database_path=canonical).unchanged == 5


def test_candidate_without_required_team_foreign_key_is_rejected(
    tmp_path: Path,
) -> None:
    canonical = tmp_path / "canonical.sqlite3"
    candidate = tmp_path / "candidate.sqlite3"
    previous_batch = _batch(2023, "2023nyro", 100)
    candidate_batch = _batch(2024, "2024nyro", 200)

    ingest_historic_event(previous_batch, database_path=canonical)
    ingest_historic_event(candidate_batch, database_path=candidate)
    with sqlite3.connect(candidate) as connection:
        connection.execute("DROP TABLE match_alliance_teams")
        connection.execute(
            "CREATE TABLE match_alliance_teams ("
            "match_key TEXT NOT NULL, alliance TEXT NOT NULL, "
            "position INTEGER NOT NULL, team_number INTEGER NOT NULL, "
            "PRIMARY KEY (match_key, alliance, position))"
        )

    with pytest.raises(
        CandidateDatabaseValidationError,
        match="match_alliance_teams.*team_number.*must reference",
    ):
        promote_historic_event_database(candidate, canonical)

    assert ingest_historic_event(previous_batch, database_path=canonical).unchanged == 5
