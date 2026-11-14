import sqlite3

import config
import db


def test_init_db_renames_legacy_tba_tables(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy.db"
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", database_path)

    with sqlite3.connect(database_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(
            """
            CREATE TABLE teams (team_number INTEGER PRIMARY KEY);
            CREATE TABLE events (event_key TEXT PRIMARY KEY);
            CREATE TABLE event_teams (
                event_key TEXT REFERENCES events(event_key),
                team_number INTEGER REFERENCES teams(team_number),
                PRIMARY KEY (event_key, team_number)
            );
            CREATE TABLE matches (
                match_key TEXT PRIMARY KEY,
                event_key TEXT REFERENCES events(event_key)
            );
            CREATE TABLE rankings (
                event_key TEXT REFERENCES events(event_key),
                team_number INTEGER REFERENCES teams(team_number),
                PRIMARY KEY (event_key, team_number)
            );
            CREATE TABLE raw_api_cache (
                url TEXT PRIMARY KEY,
                etag TEXT,
                response_json TEXT,
                fetched_at INTEGER
            );
            INSERT INTO teams VALUES (578);
            INSERT INTO events VALUES ('2026nyro');
            INSERT INTO event_teams VALUES ('2026nyro', 578);
            INSERT INTO matches VALUES ('2026nyro_qm1', '2026nyro');
            INSERT INTO rankings VALUES ('2026nyro', 578);
            INSERT INTO raw_api_cache VALUES ('/event/2026nyro', 'etag', '{}', 1);
            """
        )

    db.init_db()

    with db.get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {
            "tba_teams",
            "tba_events",
            "tba_event_teams",
            "tba_matches",
            "tba_rankings",
            "raw_tba_api_data",
        } <= tables
        assert not {
            "teams",
            "events",
            "event_teams",
            "matches",
            "rankings",
            "raw_api_cache",
        } & tables
        assert conn.execute(
            "SELECT team_number FROM tba_teams"
        ).fetchone()["team_number"] == 578
        assert conn.execute(
            "SELECT match_key FROM tba_matches"
        ).fetchone()["match_key"] == "2026nyro_qm1"
        assert conn.execute(
            "SELECT url FROM raw_tba_api_data"
        ).fetchone()["url"] == "/event/2026nyro"
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    assert db.get_etag("/event/2026nyro") == "etag"
    assert db.get_cached_response("/event/2026nyro") == {}
