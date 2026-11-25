from backend.historic_ingestion import ingest_historic_event


def test_replaying_one_historic_event_is_unchanged():
    batch = {
        "season": {"year": 2024},
        "event": {"key": "2024nyro", "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
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

    first = ingest_historic_event(batch)
    replay = ingest_historic_event(batch)

    assert first.created == 4
    assert replay.created == 0
    assert replay.unchanged == 4
