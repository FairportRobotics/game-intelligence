# Graph Report - impl-ticket5  (2026-11-25)

## Corpus Check
- 22 files · ~48,290 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 189 nodes · 271 edges · 11 communities (7 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.92)
- Token cost: 10,200 input · 5,200 output

## Graph Freshness
- Built from commit: `3855b331`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Competition Domain and Selection
- FRC Events API
- Engineering Standards
- TrueSkill[¶](#trueskill "Permalink to this headline")
- Changelog[¶](#changelog "Permalink to this headline")
- historic_ingestion.py
- frc-api-docs.firstinspires.org.md
- Graphify Navigation Instructions
- Project Overview

## God Nodes (most connected - your core abstractions)
1. `FRC Events API` - 28 edges
2. `Game Intelligence domain glossary` - 26 edges
3. `ingest_historic_event()` - 17 edges
4. `Changelog[¶](#changelog "Permalink to this headline")` - 15 edges
5. `NormalizedHistoricBatch` - 11 edges
6. `HistoricIngestionValidationError` - 9 edges
7. `GETScore Details` - 9 edges
8. `Webhooks` - 8 edges
9. `Engineering Standards` - 8 edges
10. `TrueSkill[¶](#trueskill "Permalink to this headline")` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Historic Event ingestion` --references--> `IngestionSummary`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion.py
- `Historic Event ingestion` --references--> `HistoricIngestionValidationError`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion.py
- `Historic Event ingestion` --references--> `ingest_historic_event()`  [INFERRED]
  docs/historic-ingestion.md → backend/historic_ingestion.py
- `test_changed_alliance_data_is_reported_as_an_update()` --uses--> `NormalizedHistoricBatch`  [INFERRED]
  tests/test_historic_ingestion.py → backend/historic_ingestion.py
- `test_empty_match_identity_fails_with_a_validation_error()` --uses--> `NormalizedHistoricBatch`  [INFERRED]
  tests/test_historic_ingestion.py → backend/historic_ingestion.py

## Import Cycles
- None detected.

## Communities (11 total, 4 thin omitted)

### Community 0 - "Competition Domain and Selection"
Cohesion: 0.07
Nodes (33): Writable event database handoff, Match result precedence and provenance, Continuous all-time and season-reset rating streams, Phase rating update policy, Alliance selection scoring and role model, Domain documentation guidance, TrueSkill Gaussian rating model, Game Intelligence domain glossary (+25 more)

### Community 1 - "FRC Events API"
Cohesion: 0.10
Nodes (40): Accept Header, Alliance Size and Role Enums, Authorization Header, AuthorizationKey, Team Avatar Data, Award Data, Basic Authentication, District and Tournament Type Enums (+32 more)

### Community 2 - "Engineering Standards"
Cohesion: 0.08
Nodes (22): Agent skills, Codebase graph, Domain docs, Engineering standards, Issue tracker, Triage labels, GitHub issue tracker conventions, Canonical triage label mapping (+14 more)

### Community 3 - "TrueSkill[¶](#trueskill "Permalink to this headline")"
Cohesion: 0.09
Nodes (22): API[¶](#api "Permalink to this headline"), Backends[¶](#backends "Permalink to this headline"), Default values[¶](#default-values "Permalink to this headline"), Draw probability helpers[¶](#draw-probability-helpers "Permalink to this headline"), Functions for the global environment[¶](#functions-for-the-global-environment "Permalink to this headline"), Further more[¶](#further-more "Permalink to this headline"), Head-to-head (1 vs. 1) match rule[¶](#head-to-head-1-vs-1-match-rule "Permalink to this headline"), Head-to-head shortcuts[¶](#head-to-head-shortcuts "Permalink to this headline") (+14 more)

### Community 4 - "Changelog[¶](#changelog "Permalink to this headline")"
Cohesion: 0.13
Nodes (15): Changelog[¶](#changelog "Permalink to this headline"), Version 0.1.1[¶](#version-0-1-1 "Permalink to this headline"), Version 0.1.3[¶](#version-0-1-3 "Permalink to this headline"), Version 0.1.4[¶](#version-0-1-4 "Permalink to this headline"), Version 0.1[¶](#version-0-1 "Permalink to this headline"), Version 0.2.1[¶](#version-0-2-1 "Permalink to this headline"), Version 0.2[¶](#version-0-2 "Permalink to this headline"), Version 0.3.1[¶](#version-0-3-1 "Permalink to this headline") (+7 more)

### Community 6 - "historic_ingestion.py"
Cohesion: 0.13
Nodes (19): EventInput, HistoricIngestionValidationError, ingest_historic_event(), IngestionSummary, _initialize_database(), _json_data(), MatchInput, NormalizedHistoricBatch (+11 more)

### Community 7 - "frc-api-docs.firstinspires.org.md"
Cohesion: 0.22
Nodes (8): Authorization, Documentation Notes, FRC Events, HTTP401 and Authorization, Last-Modified, FMS-OnlyModifiedSince, and If-Modified-Since Headers, Migration and Program Notes:, Overview, Response Codes

## Knowledge Gaps
- **29 isolated node(s):** `Canonical issue triage roles`, `Writable event database handoff`, `Alliance`, `Alliance captain`, `EPA` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 87 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrueSkill[¶](#trueskill "Permalink to this headline")` connect `TrueSkill[¶](#trueskill "Permalink to this headline")` to `Changelog[¶](#changelog "Permalink to this headline")`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `NormalizedHistoricBatch` (e.g. with `test_changed_alliance_data_is_reported_as_an_update()` and `test_empty_match_identity_fails_with_a_validation_error()`) actually correct?**
  _`NormalizedHistoricBatch` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Canonical issue triage roles`, `Writable event database handoff`, `Alliance` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Competition Domain and Selection` be split into smaller, more focused modules?**
  _Cohesion score 0.07254623044096728 - nodes in this community are weakly interconnected._
- **Why does `Domain documentation guidance` connect `Competition Domain and Selection` to `Engineering Standards`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Should `FRC Events API` be split into smaller, more focused modules?**
  _Cohesion score 0.09743589743589744 - nodes in this community are weakly interconnected._
- **Should `Engineering Standards` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._