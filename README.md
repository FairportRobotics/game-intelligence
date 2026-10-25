# Scouting Hub

A phone- and iPad-friendly website that gives our FRC team information about the
other teams at a competition: public data (TBA, Statbotics), our own ScoutingPASS
scouting data, and ratings we calculate (Elo, TrueSkill, OPR).

**Read `docs/design.md` first.** This README is the quick start.

## Quick start (about 10 minutes)

```bash
git clone https://github.com/FairportRobotics/game-intelligence
cd game-intelligence
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit .env (add your TBA key, our team number)
python seed/load_past_event.py   # sample data (still a TODO - see the file!)
python run.py
```

Open http://localhost:5000 and enter the passcode from your `.env` file.
Phones and iPads on the same router can use `http://<laptop-ip>:5000`.

Run the tests with `pytest`. Keep them passing.

## What is in each folder

| Folder / file | Purpose |
|---|---|
| `run.py` | Starts the web app |
| `config.py`, `.env` | Settings and secrets (the real `.env` is never committed) |
| `db.py`, `schema.sql` | Database connection and table definitions *(added to the plan's tree)* |
| `prefetch/` | Loads teams, schedule, and Statbotics EPA **before** the event |
| `ingest/` | Polls TBA/FIRST **during** the event (quietly does nothing if offline) |
| `scanning/` | Parses and checks QR-scanner text, saves it as scouting data |
| `metrics/` | OPR, Elo, TrueSkill, scouted averages. Results are saved in `team_metrics` |
| `exports/` | Page snapshots and database copies (our backup plan) |
| `web/` | The Flask app: `routes/` (pages), `templates/` (HTML), `static/` (CSS/JS) |
| `seed/` | Sample data for developing without a live event |
| `tests/` | pytest tests; `tests/samples/` holds real scans and API responses |
| `wheelhouse/` | Python packages saved for offline installs |
| `docs/` | Design document |

## Rules of the road

1. **The web app never calls TBA, Statbotics, or FIRST.** Only `prefetch/` and `ingest/` do.
2. **Everything must work with no internet.** No CDN links. Put libraries in `web/static/vendor/`.
3. **Never commit `.env`** or any API key.
4. **Save raw data first** (`raw_scans`, `raw_api_cache`).
5. **Always use `?` placeholders in SQL.** Never paste values into SQL strings.
6. **Small pull requests.** One feature, one branch, one reviewer.

## Where to start (suggested tasks)

| Level | Tasks |
|---|---|
| Beginner | Download JS/CSS into `web/static/vendor/`; style the team list; fill in `elo.expected_score()`; write `db.data_freshness()` |
| Intermediate | `ingest/tba_client.py`; `prefetch/prefetch_event.py`; `scanning/parser.py` (against real samples); schedule CSV import; match prep page; Elo/TrueSkill/OPR |
| Advanced | Idempotent scan importer; pick list weights engine; `exports/snapshot.py`; `exports/db_sync.py`; scouted-total validation |

Search the code for `TODO` to find work. Each stub file has a docstring that says
what belongs in it.

```bash
grep -rn "TODO" --include=*.py --include=*.html .
```

## Offline checklist (night before an event)

- [ ] `python -m prefetch.prefetch_event`
- [ ] Turn wifi off; confirm `python run.py` works and every page loads
- [ ] Copy the database to the standby laptop (`python -m exports.db_sync`) and test it
- [ ] Export snapshots (`python -m exports.snapshot`) and screenshot the pick list
- [ ] Test the scanner and the manual score entry page

## Making a package folder for offline installs

```bash
pip download -r requirements.txt -d wheelhouse
# On an offline laptop:
pip install --no-index --find-links=wheelhouse -r requirements.txt
```
