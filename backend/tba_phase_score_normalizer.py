"""Normalize TBA season-specific score breakdowns into phase-attributable scores."""

from __future__ import annotations

PhaseScores = dict[str, dict[str, int]]

_END_GAME_FIELDS = {
    2015: (("endgamePoints",), ("endgame_points",)),
    2016: (("endgamePoints",), ("endgame_points",)),
    2017: (("endgamePoints",), ("endgame_points",)),
    2018: (("endgamePoints",), ("endgame_points",)),
    2019: (
        ("habClimbPoints",),
        ("endgamePoints",),
        ("endgame_points",),
    ),
    2020: (("endgamePoints",), ("endgame_points",)),
    2022: (("endgamePoints",), ("endgame_points",)),
    2023: (
        ("endGameChargeStationPoints", "endGameParkPoints"),
        ("endgamePoints",),
        ("endgame_points",),
    ),
    2024: (
        (
            "endGameHarmonyPoints",
            "endGameNoteInTrapPoints",
            "endGameOnStagePoints",
            "endGameParkPoints",
            "endGameSpotLightBonusPoints",
        ),
        ("endgamePoints",),
        ("endgame_points",),
    ),
    2025: (
        ("endGameBargePoints",),
        ("endgamePoints",),
        ("endgame_points",),
    ),
    2026: (
        ("endGameTowerPoints",),
        ("endgamePoints",),
        ("endgame_points",),
    ),
}
_AUTO_KEYS = ("autoPoints", "auto_points", "totalAutoPoints")
_TELEOP_KEYS = ("teleopPoints", "teleop_points", "totalTeleopPoints")


def normalize_tba_phase_scores(breakdown: object, season_year: int) -> PhaseScores:
    if not isinstance(breakdown, dict):
        return {}
    red = breakdown.get("red")
    blue = breakdown.get("blue")
    if not isinstance(red, dict) or not isinstance(blue, dict):
        return {}

    phase_scores: PhaseScores = {"red": {}, "blue": {}}
    end_game_fields = _END_GAME_FIELDS.get(season_year, ())
    for alliance, values in (("red", red), ("blue", blue)):
        auto_score = _first_score(values, _AUTO_KEYS)
        if auto_score is not None:
            phase_scores[alliance]["autonomous"] = auto_score
        end_game_score = _first_sum_scores(values, end_game_fields)
        if end_game_score is not None:
            phase_scores[alliance]["end_game"] = end_game_score
        teleop_total = _first_score(values, _TELEOP_KEYS)
        if teleop_total is not None and end_game_score is not None:
            teleop_score = teleop_total - end_game_score
            if teleop_score >= 0:
                phase_scores[alliance]["teleop"] = teleop_score
    return phase_scores


def _first_score(values: dict[str, object], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        if key in values:
            score = values[key]
            return score if type(score) is int and score >= 0 else None
    return None


def _sum_scores(values: dict[str, object], keys: tuple[str, ...]) -> int | None:
    scores = [_first_score(values, (key,)) for key in keys]
    if any(score is None for score in scores):
        return None
    return sum(score for score in scores if score is not None)


def _first_sum_scores(
    values: dict[str, object], alternatives: tuple[tuple[str, ...], ...]
) -> int | None:
    for fields in alternatives:
        score = _sum_scores(values, fields)
        if score is not None:
            return score
    return None
