"""Rebuild and read persisted all-time and season team rating streams."""

from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Literal

_ELO_INITIAL = 1500.0
_ELO_K = 32.0
_TRUESKILL_MU = 25.0
_TRUESKILL_SIGMA = 25.0 / 3.0
_TRUESKILL_BETA = 25.0 / 6.0
_TRUESKILL_TAU = 25.0 / 300.0
_TRUESKILL_DRAW_PROBABILITY = 0.1
_NORMAL = NormalDist()

RatingScope = Literal["all_time", "season"]


@dataclass(frozen=True)
class TeamRating:
    """A team's persisted Elo and TrueSkill estimates for one rating stream."""

    scope: RatingScope
    season_year: int | None
    elo: float
    trueskill_mu: float
    trueskill_sigma: float


@dataclass(frozen=True)
class _Match:
    key: str
    event_key: str
    season_year: int
    phase: str
    number: int
    red: tuple[int, ...]
    blue: tuple[int, ...]
    red_score: int
    blue_score: int


@dataclass
class _Rating:
    elo: float = _ELO_INITIAL
    mu: float = _TRUESKILL_MU
    sigma: float = _TRUESKILL_SIGMA


class RatingDataError(ValueError):
    """The canonical database does not contain usable Match history."""


def _create_rating_table(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS team_ratings (
            team_number INTEGER NOT NULL REFERENCES teams(number),
            scope TEXT NOT NULL CHECK (scope IN ('all_time', 'season')),
            season_year INTEGER,
            elo REAL NOT NULL,
            trueskill_mu REAL NOT NULL,
            trueskill_sigma REAL NOT NULL,
            CHECK (
                (scope = 'all_time' AND season_year IS NULL)
                OR (scope = 'season' AND season_year IS NOT NULL)
            )
        );
        CREATE UNIQUE INDEX IF NOT EXISTS team_ratings_identity
            ON team_ratings (team_number, scope, COALESCE(season_year, 0));
        """
    )


def _team_numbers(value: object, match_key: str, alliance: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise RatingDataError(
            f"Match {match_key!r} must have a non-empty {alliance} alliance"
        )
    if any(type(number) is not int or number <= 0 for number in value):
        raise RatingDataError(
            f"Match {match_key!r} has an invalid Team in its {alliance} alliance"
        )
    if len(set(value)) != len(value):
        raise RatingDataError(
            f"Match {match_key!r} has a duplicate Team in its {alliance} alliance"
        )
    return tuple(value)


def _parse_match(
    key: str, event_key: str, season_year: int, phase: str, data_json: str
) -> _Match | None:
    if phase not in {"qualification", "playoff"}:
        return None
    try:
        data = json.loads(data_json)
    except (TypeError, ValueError) as error:
        raise RatingDataError(f"Match {key!r} has invalid canonical data") from error
    if not isinstance(data, dict):
        raise RatingDataError(f"Match {key!r} has invalid canonical data")

    result = data.get("result")
    if result is None:
        return None
    if not isinstance(result, dict):
        raise RatingDataError(f"Match {key!r} has an invalid official result")
    red_score = result.get("red_score")
    blue_score = result.get("blue_score")
    if (
        type(red_score) is not int
        or red_score < 0
        or type(blue_score) is not int
        or blue_score < 0
    ):
        raise RatingDataError(f"Match {key!r} has an invalid official result")

    number = data.get("number")
    if type(number) is not int or number <= 0:
        raise RatingDataError(f"Match {key!r} has an invalid Match number")
    red = _team_numbers(data.get("red"), key, "red")
    blue = _team_numbers(data.get("blue"), key, "blue")
    if set(red).intersection(blue):
        raise RatingDataError(f"Match {key!r} lists a Team on both alliances")
    return _Match(
        key,
        event_key,
        season_year,
        phase,
        number,
        red,
        blue,
        red_score,
        blue_score,
    )


def _load_matches(connection: sqlite3.Connection) -> list[_Match]:
    try:
        rows = connection.execute(
            "SELECT m.key, m.event_key, e.season_year, m.phase, m.data "
            "FROM matches AS m JOIN events AS e ON e.key = m.event_key"
        ).fetchall()
    except sqlite3.Error as error:
        raise RatingDataError(
            "The database must contain canonical seasons, events, and matches"
        ) from error

    matches: list[_Match] = []
    for key, event_key, season_year, phase, data_json in rows:
        if (
            not isinstance(key, str)
            or not isinstance(event_key, str)
            or type(season_year) is not int
            or not isinstance(phase, str)
            or not isinstance(data_json, str)
        ):
            raise RatingDataError("The canonical Match table contains invalid rows")
        match = _parse_match(key, event_key, season_year, phase, data_json)
        if match is not None:
            matches.append(match)
    matches.sort(
        key=lambda match: (
            match.season_year,
            match.event_key,
            0 if match.phase == "qualification" else 1,
            match.number,
            match.key,
        )
    )
    return matches


def _rating_for(ratings: dict[int, _Rating], team_number: int) -> _Rating:
    if team_number not in ratings:
        ratings[team_number] = _Rating()
    return ratings[team_number]


def _update_elo(
    ratings: dict[int, _Rating],
    red: tuple[int, ...],
    blue: tuple[int, ...],
    red_score: int,
    blue_score: int,
) -> None:
    red_mean = sum(_rating_for(ratings, number).elo for number in red) / len(red)
    blue_mean = sum(_rating_for(ratings, number).elo for number in blue) / len(blue)
    red_expectation = 1.0 / (1.0 + 10.0 ** ((blue_mean - red_mean) / 400.0))
    red_result = 0.5 if red_score == blue_score else float(red_score > blue_score)
    adjustment = _ELO_K * (red_result - red_expectation)
    for team_number in red:
        _rating_for(ratings, team_number).elo += adjustment
    for team_number in blue:
        _rating_for(ratings, team_number).elo -= adjustment


def _pdf(value: float) -> float:
    return math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)


def _win_correction(value: float) -> tuple[float, float]:
    probability = _NORMAL.cdf(value)
    if probability < 1e-14:
        inverse_mills = -value + 1.0 / -value
        return inverse_mills, inverse_mills * (inverse_mills + value)
    v = _pdf(value) / probability
    return v, v * (v + value)


def _draw_correction(value: float, margin: float) -> tuple[float, float]:
    lower = value - margin
    upper = value + margin
    probability = _NORMAL.cdf(upper) - _NORMAL.cdf(lower)
    if probability < 1e-14:
        v = -value
        return v, 1.0
    lower_pdf = _pdf(lower)
    upper_pdf = _pdf(upper)
    v = (lower_pdf - upper_pdf) / probability
    w = v * v + (upper * upper_pdf - lower * lower_pdf) / probability
    return v, w


def _update_trueskill(
    ratings: dict[int, _Rating],
    red: tuple[int, ...],
    blue: tuple[int, ...],
    red_score: int,
    blue_score: int,
) -> None:
    red_ratings = [_rating_for(ratings, number) for number in red]
    blue_ratings = [_rating_for(ratings, number) for number in blue]
    participants = (*red_ratings, *blue_ratings)
    variances = [rating.sigma**2 + _TRUESKILL_TAU**2 for rating in participants]
    performance_variance = sum(variance + _TRUESKILL_BETA**2 for variance in variances)
    c = math.sqrt(performance_variance)
    mean_difference = sum(rating.mu for rating in red_ratings) - sum(
        rating.mu for rating in blue_ratings
    )
    draw_margin = (
        _NORMAL.inv_cdf((1.0 + _TRUESKILL_DRAW_PROBABILITY) / 2.0)
        * _TRUESKILL_BETA
        * math.sqrt(len(participants))
    )

    if red_score == blue_score:
        v, w = _draw_correction(mean_difference / c, draw_margin / c)
    else:
        red_won = red_score > blue_score
        oriented_difference = mean_difference if red_won else -mean_difference
        v, w = _win_correction(oriented_difference / c - draw_margin / c)
        if not red_won:
            v = -v

    for rating, variance in zip(
        red_ratings, variances[: len(red_ratings)], strict=True
    ):
        rating.mu += variance / c * v
        rating.sigma = math.sqrt(
            variance * max(0.0, 1.0 - variance / performance_variance * w)
        )
    for rating, variance in zip(
        blue_ratings, variances[len(red_ratings) :], strict=True
    ):
        rating.mu -= variance / c * v
        rating.sigma = math.sqrt(
            variance * max(0.0, 1.0 - variance / performance_variance * w)
        )


def _update_stream(ratings: dict[int, _Rating], match: _Match) -> None:
    _update_elo(ratings, match.red, match.blue, match.red_score, match.blue_score)
    _update_trueskill(ratings, match.red, match.blue, match.red_score, match.blue_score)


def rebuild_ratings(database_path: str | Path) -> None:
    """Recompute every all-time and season rating from canonical Match records.

    Rebuilding replaces the persisted rating table in one transaction, so
    corrected Match data replays deterministically without duplicate updates.
    """
    connection = sqlite3.connect(database_path)
    try:
        _create_rating_table(connection)
        matches = _load_matches(connection)
        all_time: dict[int, _Rating] = {}
        seasons: dict[int, dict[int, _Rating]] = {}
        for match in matches:
            _update_stream(all_time, match)
            _update_stream(seasons.setdefault(match.season_year, {}), match)

        with connection:
            connection.execute("DELETE FROM team_ratings")
            for team_number, rating in sorted(all_time.items()):
                connection.execute(
                    "INSERT INTO team_ratings "
                    "(team_number, scope, season_year, elo, trueskill_mu, "
                    "trueskill_sigma) VALUES (?, 'all_time', NULL, ?, ?, ?)",
                    (team_number, rating.elo, rating.mu, rating.sigma),
                )
            for season_year, season_ratings in sorted(seasons.items()):
                for team_number, rating in sorted(season_ratings.items()):
                    connection.execute(
                        "INSERT INTO team_ratings "
                        "(team_number, scope, season_year, elo, trueskill_mu, "
                        "trueskill_sigma) VALUES (?, 'season', ?, ?, ?, ?)",
                        (
                            team_number,
                            season_year,
                            rating.elo,
                            rating.mu,
                            rating.sigma,
                        ),
                    )
    finally:
        connection.close()


def get_team_ratings(
    database_path: str | Path, team_number: int
) -> tuple[TeamRating, ...]:
    """Return a Team's all-time and season rating snapshots, if rebuilt."""
    try:
        with sqlite3.connect(database_path) as connection:
            rows = connection.execute(
                "SELECT scope, season_year, elo, trueskill_mu, trueskill_sigma "
                "FROM team_ratings WHERE team_number = ? "
                "ORDER BY CASE scope WHEN 'all_time' THEN 0 ELSE 1 END, "
                "season_year",
                (team_number,),
            ).fetchall()
    except sqlite3.Error as error:
        raise RatingDataError(
            "Ratings have not been built in this canonical database"
        ) from error
    return tuple(
        TeamRating(
            scope=row[0],
            season_year=row[1],
            elo=row[2],
            trueskill_mu=row[3],
            trueskill_sigma=row[4],
        )
        for row in rows
    )
