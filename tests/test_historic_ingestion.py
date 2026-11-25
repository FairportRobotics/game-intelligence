import json
import sqlite3

import pytest

from backend.historic_ingestion import (
    HistoricIngestionValidationError,
    NormalizedHistoricBatch,
    ingest_historic_event,
    list_playoff_roster_results,
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


def test_complete_playoff_roster_classifies_each_team_with_source_provenance(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
            {"number": 254, "name": "The Cheesy Poofs"},
            {"number": 1678, "name": "Citrus Circuits"},
            {"number": 4414, "name": "High Tide"},
        ],
        "matches": [],
        "source": "tba",
        "playoff_rosters": {
            "complete": True,
            "alliances": [
                {"number": 1, "teams": [578, 100, 254, 1678]},
            ],
        },
    }

    ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")
    results = list_playoff_roster_results(
        "2024nyro", database_path=tmp_path / "canonical.sqlite3"
    )

    assert [
        (result.team_number, result.role, result.source, result.complete)
        for result in results
    ] == [
        (100, "First pick", "tba", True),
        (254, "Second pick", "tba", True),
        (578, "Captain", "tba", True),
        (1678, "Third pick", "tba", True),
        (4414, "Not selected", "tba", True),
    ]


def test_incomplete_playoff_roster_does_not_infer_not_selected(tmp_path):
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
            {"number": 254, "name": "The Cheesy Poofs"},
        ],
        "matches": [],
        "source": "tba",
        "playoff_rosters": {
            "complete": False,
            "alliances": [{"number": 1, "teams": [578, 100]}],
        },
    }

    ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")
    results = list_playoff_roster_results(
        "2024nyro", database_path=tmp_path / "canonical.sqlite3"
    )

    assert [
        (result.team_number, result.role, result.source, result.complete)
        for result in results
    ] == [
        (100, "First pick", "tba", False),
        (578, "Captain", "tba", False),
    ]


def test_complete_roster_from_first_is_reconciled_over_incomplete_tba_data(
    tmp_path,
):
    database = tmp_path / "canonical.sqlite3"
    base: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
            {"number": 254, "name": "The Cheesy Poofs"},
        ],
        "matches": [],
        "source": "tba",
    }
    tba_batch = base.copy()
    tba_batch["playoff_rosters"] = {
        "complete": False,
        "alliances": [{"number": 1, "teams": [578]}],
    }
    first_batch = base.copy()
    first_batch["source"] = "first"
    first_batch["playoff_rosters"] = {
        "complete": True,
        "alliances": [{"number": 1, "teams": [578, 100]}],
    }

    ingest_historic_event(tba_batch, database_path=database)
    ingest_historic_event(first_batch, database_path=database)

    results = list_playoff_roster_results("2024nyro", database_path=database)
    assert [
        (result.team_number, result.role, result.source, result.complete)
        for result in results
    ] == [
        (100, "First pick", "first", True),
        (254, "Not selected", "first", True),
        (578, "Captain", "first", True),
    ]


def test_incomplete_refresh_does_not_replace_a_complete_source_roster(tmp_path):
    database = tmp_path / "canonical.sqlite3"
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
            {"number": 254, "name": "The Cheesy Poofs"},
        ],
        "matches": [],
        "source": "tba",
        "playoff_rosters": {
            "complete": True,
            "alliances": [{"number": 1, "teams": [578, 100]}],
        },
    }

    ingest_historic_event(batch, database_path=database)
    batch["playoff_rosters"] = {
        "complete": False,
        "alliances": [{"number": 1, "teams": [578]}],
    }
    ingest_historic_event(batch, database_path=database)

    results = list_playoff_roster_results("2024nyro", database_path=database)
    assert [
        (result.team_number, result.role, result.source, result.complete)
        for result in results
    ] == [
        (100, "First pick", "tba", True),
        (254, "Not selected", "tba", True),
        (578, "Captain", "tba", True),
    ]


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


def test_manual_match_result_is_stored_as_a_provisional_source(tmp_path):
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
                "result": {"red_score": 40, "blue_score": 35},
            }
        ],
        "source": "manual",
    }
    database = tmp_path / "canonical.sqlite3"

    summary = ingest_historic_event(batch, database_path=database)

    with sqlite3.connect(database) as connection:
        canonical_match = connection.execute(
            "SELECT data, provenance FROM matches WHERE key = '2024nyro_qm1'"
        ).fetchone()
        stored_source = connection.execute(
            "SELECT source, data FROM match_results WHERE match_key = '2024nyro_qm1'"
        ).fetchone()

    assert summary.affected_matches == ("2024nyro_qm1",)
    assert json.loads(canonical_match[0])["result"] == {
        "red_score": 40,
        "blue_score": 35,
    }
    assert json.loads(canonical_match[1])["source"] == "manual"
    assert stored_source[0] == "manual"
    assert json.loads(stored_source[1]) == {
        "red_score": 40,
        "blue_score": 35,
    }


def test_result_precedence_is_independent_of_source_arrival_order(tmp_path):
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
                "result": {"red_score": 40, "blue_score": 35},
            }
        ],
        "source": "manual",
    }
    database = tmp_path / "canonical.sqlite3"

    manual = ingest_historic_event(batch, database_path=database)
    batch["source"] = "tba"
    batch["matches"][0]["result"] = {"red_score": 50, "blue_score": 45}
    tba = ingest_historic_event(batch, database_path=database)
    batch["source"] = "first"
    batch["matches"][0]["result"] = {"red_score": 60, "blue_score": 55}
    first = ingest_historic_event(batch, database_path=database)
    batch["source"] = "manual"
    batch["matches"][0]["result"] = {"red_score": 1, "blue_score": 0}
    lower_priority_replay = ingest_historic_event(batch, database_path=database)

    with sqlite3.connect(database) as connection:
        canonical_match = connection.execute(
            "SELECT data, provenance FROM matches WHERE key = '2024nyro_qm1'"
        ).fetchone()
        stored_sources = connection.execute(
            "SELECT source FROM match_results WHERE match_key = '2024nyro_qm1' "
            "ORDER BY source"
        ).fetchall()

    assert manual.replaced == 0
    assert tba.replaced == 1
    assert tba.affected_matches == ("2024nyro_qm1",)
    assert first.replaced == 1
    assert first.affected_matches == ("2024nyro_qm1",)
    assert lower_priority_replay.replaced == 0
    assert lower_priority_replay.affected_matches == ()
    assert json.loads(canonical_match[0])["result"] == {
        "red_score": 60,
        "blue_score": 55,
    }
    assert json.loads(canonical_match[1])["source"] == "first"
    assert stored_sources == [("first",), ("manual",), ("tba",)]
