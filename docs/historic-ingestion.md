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
