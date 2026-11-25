## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues for `FairportRobotics/game-intelligence`. See `docs/agents/issue-tracker.md`.

### Triage labels

The canonical triage labels are `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository using `GLOSSARY.md` and `docs/adr/`. See `docs/agents/domain.md`.

## Engineering standards

Follow [docs/engineering-standards.md](docs/engineering-standards.md) for TDD, deep-module design, pytest, Ruff, and Python type-checking requirements.

## Codebase graph

Use the Graphify graph to query code relationships and architecture when it can help answer a codebase question: `./.venv/bin/graphify query "<question>"`. The graph is stored in `graphify-out/`; verify relevant findings against source files.
