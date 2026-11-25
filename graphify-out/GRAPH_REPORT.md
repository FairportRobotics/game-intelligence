# Graph Report - game-intelligence  (2026-11-25)

## Corpus Check
- 30 files · ~55,892 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 335 nodes · 704 edges · 18 communities (11 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 59 edges (avg confidence: 0.93)
- Token cost: 10,200 input · 5,200 output

## Graph Freshness
- Built from commit: `e32e75ff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Competition Domain and Selection
- FRC Events API
- Engineering Standards
- Changelog[¶](#changelog "Permalink to this headline")
- run_historic_ingestion
- ingest_historic_event
- frc-api-docs.firstinspires.org.md
- historic_database_promotion.py
- ratings.py
- Graphify Navigation Instructions
- Project Overview
- get_team_ratings
- tba_phase_score_normalizer.py

## God Nodes (most connected - your core abstractions)
1. `ingest_historic_event()` - 49 edges
2. `NormalizedHistoricBatch` - 35 edges
3. `FRC Events API` - 28 edges
4. `Game Intelligence domain glossary` - 26 edges
5. `run_historic_ingestion()` - 24 edges
6. `promote_historic_event_database()` - 17 edges
7. `rebuild_ratings()` - 15 edges
8. `get_team_ratings()` - 15 edges
9. `Changelog[¶](#changelog "Permalink to this headline")` - 15 edges
10. `IngestionSummary` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Historic Event ingestion` --references--> `HistoricIngestionValidationError`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion.py
- `Historic Event ingestion` --references--> `ingest_historic_event()`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion.py
- `Historic Event ingestion` --references--> `IngestionSummary`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion.py
- `Resumable ingestion runs` --references--> `RunSummary`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion_runs.py
- `Resumable ingestion runs` --references--> `run_historic_ingestion()`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion_runs.py

## Import Cycles
- None detected.

## Communities (18 total, 7 thin omitted)

### Community 0 - "Competition Domain and Selection"
Cohesion: 0.07
Nodes (36): Writable event database handoff, Match result precedence and provenance, Continuous all-time and season-reset rating streams, Phase rating update policy, Alliance selection scoring and role model, Domain documentation guidance, TrueSkill Gaussian rating model, TrueSkill partial-play weights (+28 more)

### Community 1 - "FRC Events API"
Cohesion: 0.10
Nodes (40): Accept Header, Alliance Size and Role Enums, Authorization Header, AuthorizationKey, Team Avatar Data, Award Data, Basic Authentication, District and Tournament Type Enums (+32 more)

### Community 2 - "Engineering Standards"
Cohesion: 0.08
Nodes (22): Agent skills, Codebase graph, Domain docs, Engineering standards, Issue tracker, Triage labels, GitHub issue tracker conventions, Canonical triage label mapping (+14 more)

### Community 3 - "Changelog[¶](#changelog "Permalink to this headline")"
Cohesion: 0.06
Nodes (34): API[¶](#api "Permalink to this headline"), Backends[¶](#backends "Permalink to this headline"), Changelog[¶](#changelog "Permalink to this headline"), Default values[¶](#default-values "Permalink to this headline"), Draw probability helpers[¶](#draw-probability-helpers "Permalink to this headline"), Functions for the global environment[¶](#functions-for-the-global-environment "Permalink to this headline"), Further more[¶](#further-more "Permalink to this headline"), Head-to-head (1 vs. 1) match rule[¶](#head-to-head-1-vs-1-match-rule "Permalink to this headline") (+26 more)

### Community 4 - "run_historic_ingestion"
Cohesion: 0.10
Nodes (30): IngestionSummary, _count_record(), _empty_counts(), EventIngestor, EventSource, FailureDetail, _human_summary(), _initialize_checkpoints() (+22 more)

### Community 6 - "ingest_historic_event"
Cohesion: 0.12
Nodes (31): EventInput, HistoricIngestionValidationError, ingest_historic_event(), _initialize_database(), _json_data(), list_playoff_roster_results(), _match_result_winner(), MatchInput (+23 more)

### Community 7 - "frc-api-docs.firstinspires.org.md"
Cohesion: 0.22
Nodes (8): Authorization, Documentation Notes, FRC Events, HTTP401 and Authorization, Last-Modified, FMS-OnlyModifiedSince, and If-Modified-Since Headers, Migration and Program Notes:, Overview, Response Codes

### Community 8 - "historic_database_promotion.py"
Cohesion: 0.14
Nodes (16): _backup_path(), _candidate_issues(), CandidateDatabaseValidationError, _connect_readonly(), _copy_database(), DatabasePromotionError, _preserve_canonical(), promote_historic_event_database() (+8 more)

### Community 9 - "ratings.py"
Cohesion: 0.15
Nodes (17): parse_match_timestamp(), _create_rating_table(), _draw_correction(), _load_matches(), _Match, _parse_match(), _pdf(), _phase_scores() (+9 more)

### Community 13 - "get_team_ratings"
Cohesion: 0.26
Nodes (10): get_team_ratings(), rebuild_ratings(), TeamRating, Team ratings, test_corrected_official_result_rebuilds_history_without_duplicate_updates(), test_draw_updates_team_ratings_using_documented_trueskill_defaults(), test_match_order_is_stable_and_season_streams_reset(), test_rebuilding_phase_ratings_normalizes_tba_subtotals() (+2 more)

### Community 17 - "tba_phase_score_normalizer.py"
Cohesion: 0.48
Nodes (4): _first_score(), _first_sum_scores(), normalize_tba_phase_scores(), _sum_scores()

## Knowledge Gaps
- **29 isolated node(s):** `Canonical issue triage roles`, `Writable event database handoff`, `TrueSkill partial-play weights`, `Alliance`, `Alliance captain` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 116 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ingest_historic_event()` connect `ingest_historic_event` to `run_historic_ingestion`, `historic_database_promotion.py`, `ratings.py`, `get_team_ratings`, `tba_phase_score_normalizer.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `ingest_historic_event()` (e.g. with `Historic Event ingestion` and `test_exhausted_transient_failures_are_reported_without_exception_secrets()`) actually correct?**
  _`ingest_historic_event()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Canonical issue triage roles`, `Writable event database handoff`, `TrueSkill partial-play weights` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Competition Domain and Selection` be split into smaller, more focused modules?**
  _Cohesion score 0.06504065040650407 - nodes in this community are weakly interconnected._
- **Why does `TrueSkill[¶](#trueskill "Permalink to this headline")` connect `Changelog[¶](#changelog "Permalink to this headline")` to `Competition Domain and Selection`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `NormalizedHistoricBatch` (e.g. with `EventIngestor` and `SourceResult`) actually correct?**
  _`NormalizedHistoricBatch` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Should `FRC Events API` be split into smaller, more focused modules?**
  _Cohesion score 0.09743589743589744 - nodes in this community are weakly interconnected._