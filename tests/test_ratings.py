import pytest

from backend.historic_ingestion import (
    HistoricIngestionValidationError,
    NormalizedHistoricBatch,
    TeamInput,
    ingest_historic_event,
)
from backend.ratings import get_team_ratings, rebuild_ratings


def test_rated_match_requires_an_offset_aware_timestamp(tmp_path):
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
        "source": "tba",
    }

    with pytest.raises(HistoricIngestionValidationError, match="timestamp"):
        ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")
    batch["matches"][0]["timestamp"] = "2024-03-15T10:00:00"
    with pytest.raises(HistoricIngestionValidationError, match="timezone"):
        ingest_historic_event(batch, database_path=tmp_path / "canonical.sqlite3")


def test_rebuilding_ratings_persists_independent_phase_streams(tmp_path):
    database = tmp_path / "canonical.sqlite3"
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
                "timestamp": "2024-03-15T10:00:00Z",
                "result": {"red_score": 40, "blue_score": 35},
                "phase_scores": {
                    "red": {"autonomous": 20, "teleop": 15, "end_game": 5},
                    "blue": {"autonomous": 10, "teleop": 20, "end_game": 5},
                },
            }
        ],
        "source": "first",
    }

    ingest_historic_event(batch, database_path=database)

    rebuild_ratings(database)

    autonomous = get_team_ratings(database, 578, phase="autonomous")
    teleop = get_team_ratings(database, 578, phase="teleop")
    end_game = get_team_ratings(database, 578, phase="end_game")
    assert tuple(rating.scope for rating in autonomous) == ("all_time", "season")
    assert tuple(rating.elo for rating in autonomous) == (1516.0, 1516.0)
    assert tuple(rating.elo for rating in teleop) == (1484.0, 1484.0)
    assert tuple(rating.elo for rating in end_game) == (1500.0, 1500.0)
    assert tuple(rating.phase for rating in autonomous) == (
        "autonomous",
        "autonomous",
    )
    assert tuple(rating.elo for rating in get_team_ratings(database, 578)) == (
        1516.0,
        1516.0,
    )


def test_rebuilding_phase_ratings_normalizes_tba_subtotals(tmp_path):
    database = tmp_path / "canonical.sqlite3"
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2018},
        "event": {"key": "2018nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": "2018nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100],
                "timestamp": "2018-03-15T10:00:00Z",
                "result": {"red_score": 100, "blue_score": 90},
                "score_breakdown": {
                    "red": {
                        "autoPoints": 10,
                        "teleopPoints": 50,
                        "endgamePoints": 20,
                        "foulPoints": 99,
                        "adjustPoints": 80,
                        "rp": 4,
                    },
                    "blue": {
                        "autoPoints": 10,
                        "teleopPoints": 40,
                        "endgamePoints": 20,
                        "foulPoints": 0,
                        "adjustPoints": 0,
                        "rp": 0,
                    },
                },
            }
        ],
        "source": "tba",
    }

    ingest_historic_event(batch, database_path=database)

    rebuild_ratings(database)

    assert tuple(
        rating.elo for rating in get_team_ratings(database, 578, phase="autonomous")
    ) == (1500.0, 1500.0)
    assert tuple(
        rating.elo for rating in get_team_ratings(database, 578, phase="teleop")
    ) == (1516.0, 1516.0)
    assert tuple(
        rating.elo for rating in get_team_ratings(database, 578, phase="end_game")
    ) == (1500.0, 1500.0)


def test_rebuilding_ratings_exposes_all_time_and_season_team_streams(tmp_path):
    database = tmp_path / "canonical.sqlite3"
    batch: NormalizedHistoricBatch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
            {"number": 101, "name": "Team 101"},
        ],
        "matches": [
            {
                "key": "2024nyro_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100, 101],
                "timestamp": "2024-03-15T10:00:00Z",
                "result": {"red_score": 40, "blue_score": 35},
            }
        ],
        "source": "first",
    }

    ingest_historic_event(batch, database_path=database)
    rebuild_ratings(database)

    red_ratings = get_team_ratings(database, 578)
    blue_ratings = get_team_ratings(database, 100)
    assert tuple(rating.scope for rating in red_ratings) == ("all_time", "season")
    assert tuple(rating.season_year for rating in red_ratings) == (None, 2024)
    assert tuple(rating.elo for rating in red_ratings) == (1516.0, 1516.0)
    assert tuple(rating.trueskill_mu for rating in red_ratings) == pytest.approx(
        (33.731, 33.731), abs=0.001
    )
    assert tuple(rating.trueskill_sigma for rating in red_ratings) == pytest.approx(
        (7.317, 7.317), abs=0.001
    )
    assert tuple(rating.elo for rating in blue_ratings) == (1484.0, 1484.0)
    assert tuple(rating.trueskill_mu for rating in blue_ratings) == pytest.approx(
        (16.269, 16.269), abs=0.001
    )
    assert tuple(rating.trueskill_sigma for rating in blue_ratings) == pytest.approx(
        (7.317, 7.317), abs=0.001
    )
    assert get_team_ratings(database, 101) == get_team_ratings(database, 100)


def test_match_order_is_stable_and_season_streams_reset(tmp_path):
    database = tmp_path / "canonical.sqlite3"
    teams: list[TeamInput] = [
        {"number": 578, "name": "Fairport Robotics"},
        {"number": 100, "name": "The Wildhats"},
    ]
    ingest_historic_event(
        {
            "season": {"year": 2024},
            "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
            "teams": teams,
            "matches": [
                {
                    "key": "2024nyro_qm2",
                    "type": "qualification",
                    "number": 2,
                    "red": [100],
                    "blue": [578],
                    "timestamp": "2024-03-15T10:00:00Z",
                    "result": {"red_score": 40, "blue_score": 35},
                },
                {
                    "key": "2024nyro_qm1",
                    "type": "qualification",
                    "number": 1,
                    "red": [578],
                    "blue": [100],
                    "timestamp": "2024-03-15T11:00:00Z",
                    "result": {"red_score": 40, "blue_score": 35},
                },
            ],
            "source": "first",
        },
        database_path=database,
    )
    ingest_historic_event(
        {
            "season": {"year": 2025},
            "event": {"key": "2025nyro", "name": "Finger Lakes Regional"},
            "teams": teams,
            "matches": [
                {
                    "key": "2025nyro_qm1",
                    "type": "qualification",
                    "number": 1,
                    "red": [578],
                    "blue": [100],
                    "timestamp": "2025-03-15T10:00:00Z",
                    "result": {"red_score": 40, "blue_score": 35},
                }
            ],
            "source": "first",
        },
        database_path=database,
    )

    rebuild_ratings(database)

    red_ratings = get_team_ratings(database, 578)
    blue_ratings = get_team_ratings(database, 100)
    assert tuple(rating.scope for rating in red_ratings) == (
        "all_time",
        "season",
        "season",
    )
    assert tuple(rating.season_year for rating in red_ratings) == (
        None,
        2024,
        2025,
    )
    assert tuple(rating.elo for rating in red_ratings) == pytest.approx(
        (1517.334159, 1501.469502, 1516.0)
    )
    assert red_ratings[1].elo == pytest.approx(1501.469502)
    assert tuple(rating.elo for rating in blue_ratings) == pytest.approx(
        (1482.665841, 1498.530498, 1484.0)
    )
    assert (
        red_ratings[2].trueskill_mu,
        red_ratings[2].trueskill_sigma,
    ) == pytest.approx((29.396, 7.171), abs=0.001)
    assert red_ratings[0].trueskill_mu != red_ratings[2].trueskill_mu
    assert (
        blue_ratings[2].trueskill_mu,
        blue_ratings[2].trueskill_sigma,
    ) == pytest.approx((20.604, 7.171), abs=0.001)
    assert blue_ratings[0].trueskill_mu != blue_ratings[2].trueskill_mu


def test_corrected_official_result_rebuilds_history_without_duplicate_updates(
    tmp_path,
):
    database = tmp_path / "canonical.sqlite3"
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
                "timestamp": "2024-03-15T10:00:00Z",
                "result": {"red_score": 40, "blue_score": 35},
            }
        ],
        "source": "tba",
    }

    ingest_historic_event(batch, database_path=database)
    rebuild_ratings(database)
    before_correction = get_team_ratings(database, 578)
    batch["source"] = "first"
    batch["matches"][0]["result"] = {"red_score": 30, "blue_score": 35}
    ingest_historic_event(batch, database_path=database)
    rebuild_ratings(database)
    corrected = get_team_ratings(database, 578)
    rebuild_ratings(database)

    assert before_correction[0].elo == 1516.0
    assert corrected == get_team_ratings(database, 578)
    assert tuple(rating.elo for rating in corrected) == (1484.0, 1484.0)
    assert tuple(rating.trueskill_mu for rating in corrected) == pytest.approx(
        (20.604, 20.604), abs=0.001
    )


def test_draw_updates_team_ratings_using_documented_trueskill_defaults(tmp_path):
    database = tmp_path / "canonical.sqlite3"
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
                "timestamp": "2024-03-15T10:00:00Z",
                "result": {"red_score": 40, "blue_score": 40},
            }
        ],
        "source": "first",
    }

    ingest_historic_event(batch, database_path=database)
    rebuild_ratings(database)

    for team_number in (578, 100):
        ratings = get_team_ratings(database, team_number)
        assert tuple(rating.elo for rating in ratings) == (1500.0, 1500.0)
        assert tuple(rating.trueskill_mu for rating in ratings) == (25.0, 25.0)
        assert tuple(rating.trueskill_sigma for rating in ratings) == pytest.approx(
            (6.458, 6.458), abs=0.001
        )
