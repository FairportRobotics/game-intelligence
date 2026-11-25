# Graph Report - game-intelligence  (2026-11-25)

## Corpus Check
- Corpus is ~46,692 words - fits in a single context window. You may not need a graph.

## Summary
- 104 nodes · 147 edges · 13 communities (10 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.87)
- Token cost: 10,200 input · 5,200 output

## Community Hubs (Navigation)
- Competition Domain and Selection
- FIRST Events API and Sync
- Engineering Standards and Agent Setup
- Rating Models and History
- Event Metadata Endpoints
- Match Schedule and Scoring
- Historic Ingestion Implementation
- Architecture Decisions
- Event Rankings and Advancement
- API Authentication
- Graphify Navigation Instructions
- Project Overview

## God Nodes (most connected - your core abstractions)
1. `FRC Events API` - 28 edges
2. `Game Intelligence domain glossary` - 26 edges
3. `GETScore Details` - 8 edges
4. `Domain documentation guidance` - 7 edges
5. `eventCode` - 6 edges
6. `Engineering standards` - 6 edges
7. `Phase rating update policy` - 6 edges
8. `Alliance selection scoring and role model` - 6 edges
9. `ingest_historic_event()` - 5 edges
10. `GETTeam Avatar Listings` - 5 edges

## Surprising Connections (you probably didn't know these)
- `test_replaying_one_historic_event_is_unchanged()` --calls--> `ingest_historic_event()`  [EXTRACTED]
  tests/test_historic_ingestion.py → backend/historic_ingestion.py
- `Repository agent instructions` --references--> `Domain documentation guidance`  [EXTRACTED]
  AGENTS.md → docs/agents/domain.md
- `Domain documentation guidance` --references--> `Game Intelligence domain glossary`  [EXTRACTED]
  docs/agents/domain.md → GLOSSARY.md
- `Alliance selection scoring and role model` --conceptually_related_to--> `Alliance selection`  [EXTRACTED]
  docs/adr/0005-alliance-selection-pick-lists.md → GLOSSARY.md
- `Phase rating update policy` --conceptually_related_to--> `Autonomous`  [EXTRACTED]
  docs/adr/0004-phase-specific-ratings.md → GLOSSARY.md

## Import Cycles
- None detected.

## Communities (13 total, 3 thin omitted)

### Community 0 - "Competition Domain and Selection"
Cohesion: 0.11
Nodes (23): Phase rating update policy, Alliance selection scoring and role model, Game Intelligence domain glossary, Alliance, Alliance captain, Alliance selection, Autonomous, End Game (+15 more)

### Community 1 - "FIRST Events API and Sync"
Cohesion: 0.24
Nodes (12): Accept Header, GETAPI Index, FIRST/FMS event data system, Field Management System, FMS-OnlyModifiedSince Header, FRC Events API, HTTP 200 OK, HTTP 304 Not Modified (+4 more)

### Community 2 - "Engineering Standards and Agent Setup"
Cohesion: 0.20
Nodes (10): Repository agent instructions, GitHub issue tracker conventions, Canonical triage label mapping, Canonical issue triage roles, Engineering standards, Deep-module design, Pyrefly type checking, pytest test suite (+2 more)

### Community 3 - "Rating Models and History"
Cohesion: 0.20
Nodes (9): Continuous all-time and season-reset rating streams, TrueSkill 0.4.5 documentation, TrueSkill Gaussian rating model, TrueSkill partial-play weights, TrueSkill team rating updates, All-time rating, Elo rating, Season rating (+1 more)

### Community 4 - "Event Metadata Endpoints"
Cohesion: 0.31
Nodes (9): Team Avatar Data, Award Data, GETEvent Awards, eventCode, HTTP 400 Invalid or Malformed Request, HTTP 404 Invalid Event, season, GETTeam Avatar Listings (+1 more)

### Community 5 - "Match Schedule and Scoring"
Cohesion: 0.33
Nodes (9): GETEvent Schedule, HTTP 501 Request Did Not Match API Pattern, Match Alliance Data, matchNumber, start and end match range, Match Score Data, Event Schedule Data, GETScore Details (+1 more)

### Community 6 - "Historic Ingestion Implementation"
Cohesion: 0.36
Nodes (3): ingest_historic_event(), IngestionSummary, test_replaying_one_historic_event_is_unchanged()

### Community 7 - "Architecture Decisions"
Cohesion: 0.25
Nodes (4): Writable event database handoff, Match result precedence and provenance, Domain documentation guidance, Official result

### Community 8 - "Event Rankings and Advancement"
Cohesion: 0.60
Nodes (5): GETAlliance Selection Points, Alliance Size and Role Enums, District and Tournament Type Enums, District Ranking Data, GETQual Performance Points

### Community 9 - "API Authentication"
Cohesion: 0.50
Nodes (4): Authorization Header, AuthorizationKey, Basic Authentication, HTTP 401 Unauthorized

## Knowledge Gaps
- **30 isolated node(s):** `GETAPI Index`, `AuthorizationKey`, `Accept Header`, `HTTP 200 OK`, `HTTP 500 Internal Server Error` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 35 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Game Intelligence domain glossary` connect `Competition Domain and Selection` to `Rating Models and History`, `Architecture Decisions`?**
  _High betweenness centrality (0.173) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `eventCode` (e.g. with `Team Avatar Data` and `HTTP 404 Invalid Event`) actually correct?**
  _`eventCode` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `GETAPI Index`, `AuthorizationKey`, `Accept Header` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Competition Domain and Selection` be split into smaller, more focused modules?**
  _Cohesion score 0.11462450592885376 - nodes in this community are weakly interconnected._
- **Why does `Domain documentation guidance` connect `Architecture Decisions` to `Competition Domain and Selection`, `Engineering Standards and Agent Setup`, `Rating Models and History`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `FRC Events API` connect `FIRST Events API and Sync` to `Event Rankings and Advancement`, `API Authentication`, `Event Metadata Endpoints`, `Match Schedule and Scoring`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._