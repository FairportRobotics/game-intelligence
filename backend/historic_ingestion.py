import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

MatchType = Literal["qualification", "playoff", "practice", "offseason"]
MatchResultSource = Literal["tba", "TBA", "first", "FIRST", "manual"]


class SeasonInput(TypedDict):
    year: int


class EventInput(TypedDict):
    key: str
    name: str


class TeamInput(TypedDict):
    number: int
    name: str


class MatchInput(TypedDict):
    key: str
    type: MatchType
    number: int
    red: list[int]
    blue: list[int]
    result: NotRequired[dict[str, int]]
    phase_scores: NotRequired[dict[str, object]]
    score_breakdown: NotRequired[dict[str, object]]


class NormalizedHistoricBatch(TypedDict):
    season: SeasonInput
    event: EventInput
    teams: list[TeamInput]
    matches: list[MatchInput]
    source: MatchResultSource


@dataclass(frozen=True)
class IngestionSummary:
    created: int
    unchanged: int
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    replaced: int = 0
    affected_matches: tuple[str, ...] = ()


class HistoricIngestionValidationError(ValueError):
    """Raised when a normalized historic batch lacks valid canonical data."""


def _initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS seasons (
            year INTEGER PRIMARY KEY,
            data TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS teams (
            number INTEGER PRIMARY KEY,
            data TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            key TEXT PRIMARY KEY,
            season_year INTEGER NOT NULL REFERENCES seasons(year),
            data TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS event_teams (
            event_key TEXT NOT NULL REFERENCES events(key) ON DELETE CASCADE,
            team_number INTEGER NOT NULL REFERENCES teams(number),
            PRIMARY KEY (event_key, team_number)
        );
        CREATE TABLE IF NOT EXISTS matches (
            key TEXT PRIMARY KEY,
            event_key TEXT NOT NULL REFERENCES events(key),
            phase TEXT NOT NULL,
            data TEXT NOT NULL,
            provenance TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS match_results (
            match_key TEXT NOT NULL REFERENCES matches(key) ON DELETE CASCADE,
            source TEXT NOT NULL,
            data TEXT NOT NULL,
            PRIMARY KEY (match_key, source)
        );
        CREATE TABLE IF NOT EXISTS match_alliance_teams (
            match_key TEXT NOT NULL REFERENCES matches(key) ON DELETE CASCADE,
            alliance TEXT NOT NULL CHECK (alliance IN ('red', 'blue')),
            position INTEGER NOT NULL,
            team_number INTEGER NOT NULL REFERENCES teams(number),
            PRIMARY KEY (match_key, alliance, position)
        );
        """
    )


def _json_data(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as error:
        raise HistoricIngestionValidationError(
            f"Record contains a value that cannot be persisted: {error}"
        ) from error


def _persist(
    connection: sqlite3.Connection,
    table: str,
    key_column: str,
    key: int | str,
    data: str,
    extra_columns: tuple[str, ...] = (),
    extra_values: tuple[int | str, ...] = (),
) -> str:
    selected_columns = ("data", *extra_columns)
    existing = connection.execute(
        f"SELECT {', '.join(selected_columns)} FROM {table} WHERE {key_column} = ?",
        (key,),
    ).fetchone()
    if existing is None:
        columns = (key_column, *extra_columns, "data")
        placeholders = ", ".join("?" for _ in columns)
        connection.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            (key, *extra_values, data),
        )
        return "created"
    if existing == (data, *extra_values):
        return "unchanged"
    assignments = (*extra_columns, "data")
    connection.execute(
        f"UPDATE {table} SET "
        f"{', '.join(f'{column} = ?' for column in assignments)} "
        f"WHERE {key_column} = ?",
        (*extra_values, data, key),
    )
    return "updated"


def _validate_batch(batch: NormalizedHistoricBatch) -> None:
    if not isinstance(batch, dict):
        raise HistoricIngestionValidationError("batch must be a mapping")
    if batch.get("source") not in {"tba", "TBA", "first", "FIRST", "manual"}:
        raise HistoricIngestionValidationError(
            "source must be 'FIRST', 'TBA', or 'manual'"
        )
    season = batch.get("season")
    if not isinstance(season, dict) or not isinstance(season.get("year"), int):
        raise HistoricIngestionValidationError(
            "season.year is required and must be an integer"
        )
    if isinstance(season["year"], bool) or season["year"] < 1992:
        raise HistoricIngestionValidationError("season.year must be a valid FRC year")
    event = batch.get("event")
    if (
        not isinstance(event, dict)
        or not isinstance(event.get("key"), str)
        or not event.get("key")
        or not isinstance(event.get("name"), str)
        or not event.get("name")
    ):
        raise HistoricIngestionValidationError("event.key and event.name are required")
    teams = batch.get("teams")
    if not isinstance(teams, list):
        raise HistoricIngestionValidationError("teams must be a list")
    team_numbers: set[int] = set()
    for team in teams:
        if not isinstance(team, dict):
            raise HistoricIngestionValidationError("each team must be a mapping")
        number = team.get("number")
        name = team.get("name")
        if (
            not isinstance(number, int)
            or isinstance(number, bool)
            or number <= 0
            or not isinstance(name, str)
            or not name
        ):
            raise HistoricIngestionValidationError(
                "team.number and team.name must be valid"
            )
        team_numbers.add(number)
    if len(team_numbers) != len(teams):
        raise HistoricIngestionValidationError("team numbers must be unique")
    matches = batch.get("matches")
    if not isinstance(matches, list):
        raise HistoricIngestionValidationError("matches must be a list")
    match_keys: set[str] = set()
    for match in matches:
        if not isinstance(match, dict):
            raise HistoricIngestionValidationError("each match must be a mapping")
        key = match.get("key")
        number = match.get("number")
        match_type = match.get("type")
        red = match.get("red")
        blue = match.get("blue")
        if not isinstance(key, str) or not key or key in match_keys:
            raise HistoricIngestionValidationError(
                "match.key is required and must be unique"
            )
        match_keys.add(key)
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            raise HistoricIngestionValidationError(
                "match.number must be a positive integer"
            )
        if match_type not in {"qualification", "playoff", "practice", "offseason"}:
            raise HistoricIngestionValidationError(
                f"unsupported match type: {match_type!r}"
            )
        if (
            not isinstance(red, list)
            or not red
            or not isinstance(blue, list)
            or not blue
        ):
            raise HistoricIngestionValidationError(
                "matches must have non-empty red and blue alliances"
            )
        if any(
            not isinstance(team_number, int)
            or isinstance(team_number, bool)
            or team_number not in team_numbers
            for team_number in (*red, *blue)
        ):
            raise HistoricIngestionValidationError(
                f"match {key!r} references a team absent from the batch"
            )
        if len(set(red)) != len(red) or len(set(blue)) != len(blue):
            raise HistoricIngestionValidationError(
                f"match {key!r} has a duplicate alliance Team"
            )
        if set(red).intersection(blue):
            raise HistoricIngestionValidationError(
                f"match {key!r} places a Team on both alliances"
            )
        if "result" in match:
            result = match["result"]
            if (
                not isinstance(result, dict)
                or set(result) != {"red_score", "blue_score"}
                or any(
                    not isinstance(result[alliance], int)
                    or isinstance(result[alliance], bool)
                    or result[alliance] < 0
                    for alliance in ("red_score", "blue_score")
                )
            ):
                raise HistoricIngestionValidationError(
                    f"match {key!r} result must contain non-negative integer "
                    "red_score and blue_score values"
                )


def ingest_historic_event(
    normalized_batch: NormalizedHistoricBatch,
    *,
    database_path: str | Path,
) -> IngestionSummary:
    _validate_batch(normalized_batch)
    connection = sqlite3.connect(database_path)
    try:
        _initialize_database(connection)
        counts = {"created": 0, "unchanged": 0, "updated": 0}
        affected_matches: list[str] = []
        with connection:
            season = normalized_batch["season"]
            event = normalized_batch["event"]
            source = normalized_batch["source"].lower()
            counts[
                _persist(
                    connection,
                    "seasons",
                    "year",
                    season["year"],
                    _json_data(season),
                )
            ] += 1
            team_numbers = sorted(team["number"] for team in normalized_batch["teams"])
            event_data = {
                "key": event["key"],
                "name": event["name"],
                "teams": team_numbers,
            }
            event_state = _persist(
                connection,
                "events",
                "key",
                event["key"],
                _json_data(event_data),
                ("season_year",),
                (season["year"],),
            )
            counts[event_state] += 1
            for team in normalized_batch["teams"]:
                counts[
                    _persist(
                        connection,
                        "teams",
                        "number",
                        team["number"],
                        _json_data(team),
                    )
                ] += 1
            if event_state != "unchanged":
                connection.execute(
                    "DELETE FROM event_teams WHERE event_key = ?", (event["key"],)
                )
                for team_number in team_numbers:
                    connection.execute(
                        "INSERT INTO event_teams (event_key, team_number) "
                        "VALUES (?, ?)",
                        (event["key"], team_number),
                    )
            skipped = 0
            replaced = 0
            for match in normalized_batch["matches"]:
                if match["type"] in {"practice", "offseason"}:
                    skipped += 1
                    continue
                phase = match["type"]
                match_data = dict(match)
                result = match_data.pop("result", None)
                prior_canonical = connection.execute(
                    "SELECT data, provenance, phase, event_key FROM matches "
                    "WHERE key = ?",
                    (match["key"],),
                ).fetchone()
                if prior_canonical is None:
                    connection.execute(
                        "INSERT INTO matches "
                        "(key, event_key, phase, data, provenance) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            match["key"],
                            event["key"],
                            phase,
                            _json_data(match_data),
                            _json_data({"source": source, "source_key": match["key"]}),
                        ),
                    )
                previous_winner = connection.execute(
                    "SELECT source, data FROM match_results WHERE match_key = ? "
                    "ORDER BY CASE source WHEN 'manual' THEN 0 WHEN 'tba' THEN 1 "
                    "WHEN 'first' THEN 2 ELSE -1 END DESC LIMIT 1",
                    (match["key"],),
                ).fetchone()
                if result is not None:
                    result_data = _json_data(result)
                    previous_result = connection.execute(
                        "SELECT data FROM match_results "
                        "WHERE match_key = ? AND source = ?",
                        (match["key"], source),
                    ).fetchone()
                    connection.execute(
                        "INSERT INTO match_results (match_key, source, data) "
                        "VALUES (?, ?, ?) ON CONFLICT (match_key, source) "
                        "DO UPDATE SET data = excluded.data",
                        (match["key"], source, result_data),
                    )
                    if (
                        previous_result != (result_data,)
                        and previous_winner is not None
                    ):
                        replaced += int(
                            source != previous_winner[0]
                            and {"manual": 0, "tba": 1, "first": 2}[source]
                            > {"manual": 0, "tba": 1, "first": 2}[previous_winner[0]]
                        )
                winner = connection.execute(
                    "SELECT source, data FROM match_results WHERE match_key = ? "
                    "ORDER BY CASE source WHEN 'manual' THEN 0 WHEN 'tba' THEN 1 "
                    "WHEN 'first' THEN 2 ELSE -1 END DESC LIMIT 1",
                    (match["key"],),
                ).fetchone()
                canonical_data = dict(match_data)
                canonical_source = source
                if winner is not None:
                    canonical_source = winner[0]
                    canonical_data["result"] = json.loads(winner[1])
                canonical_provenance = _json_data(
                    {"source": canonical_source, "source_key": match["key"]}
                )
                canonical_json = _json_data(canonical_data)
                canonical_record = (
                    canonical_json,
                    canonical_provenance,
                    phase,
                    event["key"],
                )
                if prior_canonical is None:
                    state = "created"
                    connection.execute(
                        "UPDATE matches SET data = ?, provenance = ?, phase = ?, "
                        "event_key = ? WHERE key = ?",
                        (*canonical_record, match["key"]),
                    )
                elif prior_canonical == canonical_record:
                    state = "unchanged"
                else:
                    state = "updated"
                    connection.execute(
                        "UPDATE matches SET data = ?, provenance = ?, phase = ?, "
                        "event_key = ? WHERE key = ?",
                        (*canonical_record, match["key"]),
                    )
                counts[state] += 1
                if prior_canonical != canonical_record and winner is not None:
                    affected_matches.append(match["key"])
                if state == "updated":
                    connection.execute(
                        "DELETE FROM match_alliance_teams WHERE match_key = ?",
                        (match["key"],),
                    )
                for alliance in ("red", "blue"):
                    for position, team_number in enumerate(match[alliance], start=1):
                        connection.execute(
                            "INSERT OR IGNORE INTO match_alliance_teams "
                            "(match_key, alliance, position, team_number) "
                            "VALUES (?, ?, ?, ?)",
                            (match["key"], alliance, position, team_number),
                        )
        return IngestionSummary(
            created=counts["created"],
            unchanged=counts["unchanged"],
            updated=counts["updated"],
            skipped=skipped,
            replaced=replaced,
            affected_matches=tuple(sorted(affected_matches)),
        )
    finally:
        connection.close()
