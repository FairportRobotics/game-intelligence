-- schema.sql - The database tables. Read by db.init_db().
--
-- RULES
--   * Use "CREATE TABLE IF NOT EXISTS" so running it twice is harmless.
--   * Outside or typed-in data carries `source` and `fetched_at` so we always
--     know where a number came from and how fresh it is.
--       source values: 'tba', 'first', 'statbotics', 'manual', 'scouted'
--   * Game-specific scouting answers live in a JSON `data` column, so we do
--     not rebuild the database every January.
--   * Changing this file after real data exists? Ask a mentor first.

-- ===== Public data =========================================================

CREATE TABLE IF NOT EXISTS teams (
    team_number  INTEGER PRIMARY KEY,
    name         TEXT,
    city         TEXT,
    state        TEXT,
    rookie_year  INTEGER
);

CREATE TABLE IF NOT EXISTS events (
    event_key   TEXT PRIMARY KEY,          -- e.g. 2026nyro
    name        TEXT,
    start_date  TEXT,
    end_date    TEXT
);

CREATE TABLE IF NOT EXISTS event_teams (
    event_key    TEXT NOT NULL REFERENCES events(event_key),
    team_number  INTEGER NOT NULL REFERENCES teams(team_number),
    PRIMARY KEY (event_key, team_number)
);

CREATE TABLE IF NOT EXISTS matches (
    match_key     TEXT PRIMARY KEY,        -- e.g. 2026nyro_qm12
    event_key     TEXT NOT NULL REFERENCES events(event_key),
    comp_level    TEXT,                    -- qm, qf, sf, f
    set_number    INTEGER,
    match_number  INTEGER,
    red1 INTEGER, red2 INTEGER, red3 INTEGER,
    blue1 INTEGER, blue2 INTEGER, blue3 INTEGER,
    red_score     INTEGER,                 -- NULL until the match is played
    blue_score    INTEGER,
    time          TEXT,
    source        TEXT,                    -- tba, first, manual, scouted
    fetched_at    TEXT
);

CREATE TABLE IF NOT EXISTS rankings (
    event_key       TEXT NOT NULL REFERENCES events(event_key),
    team_number     INTEGER NOT NULL REFERENCES teams(team_number),
    rank            INTEGER,
    record          TEXT,                  -- e.g. 5-2-0
    ranking_points  REAL,
    source          TEXT,
    fetched_at      TEXT,
    PRIMARY KEY (event_key, team_number)
);

-- Keeps the last good response from each API URL (and its ETag).
CREATE TABLE IF NOT EXISTS raw_api_cache (
    url            TEXT PRIMARY KEY,
    etag           TEXT,
    response_json  TEXT,
    fetched_at     TEXT
);

-- ===== Our scouting data ===================================================

-- EVERY scan is saved here first, exactly as typed by the scanner.
CREATE TABLE IF NOT EXISTS raw_scans (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    scanned_at     TEXT NOT NULL,
    raw_text       TEXT NOT NULL,
    status         TEXT,                   -- saved, duplicate, error
    error_message  TEXT
);

CREATE TABLE IF NOT EXISTS match_scouting (
    event_key    TEXT NOT NULL,
    match_key    TEXT NOT NULL,
    team_number  INTEGER NOT NULL,
    scout        TEXT,                     -- initials only!
    timestamp    TEXT,
    data         TEXT,                     -- JSON: all game-specific answers
    PRIMARY KEY (event_key, match_key, team_number)   -- makes re-scans an update, not a duplicate
);

CREATE TABLE IF NOT EXISTS pit_scouting (
    event_key    TEXT NOT NULL,
    team_number  INTEGER NOT NULL,
    scout        TEXT,
    timestamp    TEXT,
    data         TEXT,                     -- JSON
    PRIMARY KEY (event_key, team_number)
);

-- Which scouting fields are numbers/booleans and how to summarize them.
-- Loaded from the ScoutingPASS config JSON (see scanning/config_loader.py).
CREATE TABLE IF NOT EXISTS field_definitions (
    field_name   TEXT PRIMARY KEY,
    form         TEXT,                     -- 'match' or 'pit'
    type         TEXT,                     -- number, bool, text, choice
    aggregation  TEXT                      -- avg, pct, max, sum, none
);

-- ===== Computed data =======================================================

CREATE TABLE IF NOT EXISTS team_metrics (
    team_number  INTEGER NOT NULL,
    event_key    TEXT NOT NULL,
    metric_name  TEXT NOT NULL,            -- opr, elo, trueskill, epa_pre_event, epa_live, ...
    value        REAL,
    source       TEXT,
    updated_at   TEXT,
    PRIMARY KEY (team_number, event_key, metric_name)
);

CREATE TABLE IF NOT EXISTS picklist (
    event_key    TEXT NOT NULL,
    team_number  INTEGER NOT NULL,
    rank         INTEGER,
    tag          TEXT,                     -- first_pick, second_pick, do_not_pick, defense
    notes        TEXT,
    taken        INTEGER DEFAULT 0,        -- 1 once the team is on an alliance
    PRIMARY KEY (event_key, team_number)
);

CREATE TABLE IF NOT EXISTS weights (
    event_key    TEXT NOT NULL,
    metric_name  TEXT NOT NULL,
    weight       REAL NOT NULL,
    PRIMARY KEY (event_key, metric_name)
);
