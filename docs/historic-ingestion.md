# Historic Event ingestion

`backend.historic_ingestion.ingest_historic_event` stores one normalized TBA
Event batch in a caller-selected canonical SQLite database. Reuse the same
`database_path` to replay or update that Event; ingestion state is not held in
process memory.

The batch contains one Season, one Event, its Teams, and Matches:

```python
batch = {
    "source": "tba",
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
}
summary = ingest_historic_event(batch, database_path="canonical.sqlite3")
```

Match `type` is `qualification`, `playoff`, `practice`, or `offseason`.
Qualification and playoff Matches are persisted with their normalized
alliances and TBA match-key provenance. Practice and offseason Matches are
counted as skipped. Required identities, alliance Team references, and
supported Match types are validated before persistence; invalid batches raise
`HistoricIngestionValidationError`.

The returned `IngestionSummary` reports created, updated, unchanged, skipped,
failed, and replaced counts. Replaying an identical batch against the same
database reports its canonical records as unchanged; `failed` and `replaced`
remain zero for a successful TBA-only ingestion.

## Team ratings

`backend.ratings.rebuild_ratings` rebuilds persisted all-time and season Elo and
TrueSkill streams from canonical qualification and playoff Matches with a
resolved result. Matches without a result are skipped. The deterministic order
is Season, Event key, qualification before playoff, Match number, then Match
key. All-time ratings carry across Seasons; each season stream starts from its
own defaults. Rerunning the rebuild after corrected canonical data replaces the
rating history rather than applying duplicate updates.

Elo starts at 1500 with K=32. Alliance expectation is calculated from the mean
member ratings, and every Team on an alliance receives its same Elo adjustment.
TrueSkill uses the documented `trueskill` defaults (mu=25, sigma=25/3,
beta=25/6, tau=25/300, draw probability=0.1) with two-alliance multi-Team
updates. The implementation uses Python's standard library and adds no rating
package dependency.

```python
from backend.ratings import get_team_ratings, rebuild_ratings

rebuild_ratings("canonical.sqlite3")
ratings = get_team_ratings("canonical.sqlite3", team_number=578)
```

`get_team_ratings` returns `TeamRating` snapshots with `scope`, optional
`season_year`, `elo`, `trueskill_mu`, and `trueskill_sigma` fields.

Pass `phase="autonomous"`, `"teleop"`, or `"end_game"` to query the independent
phase streams; omitting it keeps the original overall rating query. Canonical
Match data may provide disjoint alliance totals in `phase_scores`, keyed by
`red`/`blue` and `autonomous`/`teleop`/`end_game`. When only a TBA
`score_breakdown` is present, the rebuild recognizes season-specific autonomous,
teleop, and end-game subtotal keys (including common camelCase and snake_case
aliases). Teleop is derived by subtracting an available end-game subtotal from
the teleop subtotal. The mapper does not use `totalPoints`, foul/adjustment
points, or ranking-point bonuses, and skips phases whose required scores are
unavailable; it intentionally does not infer a complete schema for every
historical Season.
## Playoff roster outcomes

Playoff roster data is optional. When available, provide the final alliance
rosters in order, with the captain first, and explicitly mark whether the
rosters are complete:

```python
batch["playoff_rosters"] = {
    "complete": True,
    "alliances": [{"number": 1, "teams": [578, 100, 254, 1678]}],
}
```

Ingested roster records remain associated with their source. The public
`list_playoff_roster_results(event_key, database_path=...)` interface prefers a
complete roster, then resolves source precedence as FIRST, TBA, and manual.
It assigns Captain and ordered pick roles; only a complete roster classifies
event Teams absent from every alliance as `Not selected`. Incomplete roster
data reports only known alliance membership and never implies an offer,
decline, or non-selection.

## Resumable ingestion runs

`backend.historic_ingestion_runs.run_historic_ingestion` processes a selected
list of Event/source pairs and stores its manifest and checkpoints in a
separate SQLite database. Reuse the same `run_id` and checkpoint database to
resume; completed Events are not fetched or ingested again. Retries of
transient source failures are bounded by `max_attempts`. A failed run summary
includes structured failure details with the Event, source, attempt count, and
a sanitized reason; adapter exception messages are not retained.

Adapters may return `SourceResult(unchanged=True)` for an unchanged or 304-style
response. In that case the canonical ingestor is not called. `RunSummary`
provides per-outcome counts and completed, skipped, and failed Event keys, plus
a concise human-readable summary. The caller supplies adapter credentials at
runtime; run manifests and checkpoints contain only Event and source
identifiers, not credentials.
