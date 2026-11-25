import pytest

from backend.historic_ingestion import (
    HistoricIngestionValidationError,
    NormalizedHistoricBatch,
    ingest_historic_event,
)


def test_replaying_one_historic_event_uses_its_canonical_database(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": "2024nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100],
            }
        ],
        "source": "tba",
    }
    database = tmp_path / "canonical.sqlite3"
    separate_database = tmp_path / "separate.sqlite3"

    first = ingest_historic_event(batch, database_path=database)
    replay = ingest_historic_event(batch, database_path=database)
    isolated = ingest_historic_event(batch, database_path=separate_database)

    assert first.created == 5
    assert replay.created == 0
    assert replay.unchanged == 5
    assert isolated.created == 5


def test_empty_match_identity_fails_with_a_validation_error(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [{"number": 578, "name": "Fairport Robotics"}],
        "matches": [
            {
                "key": "",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [578],
            }
        ],
        "source": "tba",
    }

    with pytest.raises(HistoricIngestionValidationError, match="match.key"):
        ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")


def test_match_cannot_place_a_team_on_both_alliances(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": "2024nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [578],
            }
        ],
        "source": "tba",
    }

    with pytest.raises(HistoricIngestionValidationError, match="both alliances"):
        ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")


def test_official_matches_are_ingested_and_practice_is_skipped(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": "2024nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100],
            },
            {
                "key": "2024nyro_sf1m1",
                "type": "playoff",
                "number": 1,
                "red": [578],
                "blue": [100],
            },
            {
                "key": "2024nyro_practice1",
                "type": "practice",
                "number": 1,
                "red": [578],
                "blue": [100],
            },
            {
                "key": "offseason_qm1",
                "type": "offseason",
                "number": 1,
                "red": [578],
                "blue": [100],
            },
        ],
        "source": "tba",
    }

    summary = ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")

    assert summary.created == 6
    assert summary.updated == 0
    assert summary.unchanged == 0
    assert summary.skipped == 2
    assert summary.failed == 0
    assert summary.replaced == 0


def test_changed_alliance_data_is_reported_as_an_update(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": "2024nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100],
            }
        ],
        "source": "tba",
    }
    database = tmp_path / "canonical.sqlite3"

    ingest_historic_event(batch, database_path=database)
    batch["matches"][0]["red"] = [100]
    batch["matches"][0]["blue"] = [578]
    changed = ingest_historic_event(batch, database_path=database)

    assert changed.created == 0
    assert changed.updated == 1
    assert changed.unchanged == 4
    assert changed.skipped == 0


def test_event_participating_team_changes_update_the_event(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": "2024nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100],
            }
        ],
        "source": "tba",
    }
    database = tmp_path / "canonical.sqlite3"

    ingest_historic_event(batch, database_path=database)
    batch["teams"].append({"number": 9999, "name": "New Team"})
    changed = ingest_historic_event(batch, database_path=database)

    assert changed.created == 1
    assert changed.updated == 1
    assert changed.unchanged == 4
