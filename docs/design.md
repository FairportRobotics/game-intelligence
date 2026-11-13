# FRC Team Intelligence System: Design Document

*Draft 2 for students and mentors. Written October 24, 2026. This is a living document: when we change a decision, we change this page.*

---

## 1. What are we building?

We are building a **website that works on phones and iPads** and gives our team information about the other teams at an FRC competition. It combines three kinds of data:

1. **Public data** about teams and matches (from The Blue Alliance and Statbotics).
2. **Our own scouting data** (pit and match scouting, collected with ScoutingPASS and a QR scanner).
3. **Computed metrics** such as Elo and TrueSkill that we calculate ourselves.

We will call it the **Scouting Hub** in this document. You can rename it.

### Why build it?

We already collect good scouting data. What we lack is one place where a student can quickly answer questions like *"Who are we playing with next match, and what are they good at?"* or *"Who should be our second pick?"*

### The three goals

| # | Goal | Example question it answers |
| --- | --- | --- |
| 1 | **Before the event:** information about teams in advance | "Which teams at this event are strongest? Who have we played before?" |
| 2 | **During the event:** real-time information about competitors | "What should our drive team know about the next match?" |
| 3 | **Alliance selection:** a ranked list of teams for picking | "Who is the best available robot right now?" |

### What we are *not* building (non-goals)

- We are **not** rebuilding the scouting forms. ScoutingPASS already does that well.
- We are **not** building a public product. This is for our team.
- We are **not** chasing perfect predictions. A simple, reliable tool beats a fancy one that breaks at the event.
- We are **not** using complicated infrastructure (no Docker clusters, message queues, or microservices).

---

## 2. Design principles

When you are unsure how to build something, come back to these.

1. **Keep it boring.** Use well-known tools with lots of tutorials. Boring tools are easy to learn and easy to fix at 8 PM on a Friday.
2. **One language: Python.** Everyone on the team should be able to read every part of the code.
3. **It must work with no internet.** Competition venues have bad wifi. The system must run on a laptop with its own router, and nothing it needs (data, libraries, fonts) may require the internet.
4. **Save the raw data first.** Never throw away what a scout scanned or what TBA sent. If our code has a bug, we can replay the raw data.
5. **Small pieces, small pull requests.** Each student should be able to own one page or one script from start to finish.
6. **Make mistakes visible.** Bad scouting data is normal. The system should flag it, not hide it.
7. **The app is the backup.** If one laptop fails, a second laptop is already running the same app with a recent copy of the data. Paper cannot be edited or re-sorted, so it is not a backup. A screenshot of the working app is the last resort.
8. **Outside data is a bonus, never a requirement.** TBA, Statbotics, and FIRST refresh our data when we are online. The web app never calls them directly; pages only read our local database.

---

## 3. Who uses it and how

| User | Device | What they need |
| --- | --- | --- |
| **Drive team** | iPad/phone | Match prep page: partners, opponents, strategy notes |
| **Strategy lead / pick list team** | Laptop/iPad | Ranked team list, tags, adjustable weights |
| **Scouts** | Phone/tablet running ScoutingPASS | (Unchanged: they keep using ScoutingPASS) |
| **Scouting lead** | Laptop with QR scanner | Scan page, coverage page, data-quality warnings |
| **Programmers/mentors** | Laptop | Run the ingest, metrics, and import scripts |
| **Any student** | Phone | Look up any team quickly |

---

## 4. Big picture: how the pieces fit

```
  BEFORE THE EVENT (internet available)
  The Blue Alliance ──┐
  Statbotics ─────────┼──► [ Prefetch script ] ──┐
  FIRST API ──────────┘                          │
                                                 ▼
  AT THE EVENT (internet optional)         [ SQLite database ] ◄── [ Metrics jobs ]
  TBA / FIRST, when online ─► [ Ingest ] ──►     ▲   │
  Typed-in schedule/scores ─► [ Admin pages ] ───┘   │
                                                     │
  Scouts' phones (ScoutingPASS)                      ▼
        │ QR code                              [ Flask web app ] ──► phones and iPads
        ▼                                            │
  QR scanner ─► [ Scan page ] ─► parse ─► validate ──┘

  Copy the database file to the STANDBY LAPTOP (same app, same data)
```

There are **six parts**. Each one can be built, tested, and understood on its own.

| Part | What it does | Runs when |
| --- | --- | --- |
| **Prefetch** | Before the event, pulls teams, history, the match schedule, and Statbotics EPA into the database | The week before, and again the night before the event |
| **Ingest** | Pulls live match data and rankings from TBA (or FIRST) when internet is available | Every 1-2 minutes while online; quietly skips when offline |
| **Scan importer** | Takes text from the QR scanner, parses it, checks it, and saves it | Each time a QR code is scanned |
| **Metrics** | Calculates OPR, Elo, TrueSkill, and scouted averages from whatever matches we have and saves the results | After new matches arrive |
| **Database** | Stores everything in one place | Always |
| **Web app** | Shows pages to users; reads from the database | Always |

**Important idea:** the web app mostly **reads** from the database. The heavy math happens in the metrics jobs, and the results are stored. This keeps pages fast and simple.

**Offline rule:** the web app never talks to TBA, Statbotics, or FIRST. Only the prefetch and ingest scripts do. If they fail, every page still works with the last data we saved.

---

## 5. Technology stack

| Layer | Choice | Why |
| --- | --- | --- |
| Language | **Python 3.11+** | Our team's preferred language |
| Database | **SQLite** | One file, no server, no passwords. Plenty for one event, and easy to copy to a standby laptop |
| Data access | **pandas** + SQL (or SQLAlchemy later) | Students learn SQL, which is useful everywhere |
| Web framework | **Flask** with **Jinja2** templates | Simple, well documented, easy to teach |
| Interactivity | **HTMX** | Auto-refresh and form submits without writing JavaScript |
| Styling | **Pico.css** (or Bootstrap) | Looks good on phones with almost no CSS work |
| Charts | **Plotly** | Interactive charts from Python |
| Metrics | **trueskill** package, our own Elo and OPR code, **statbotics** package (prefetch only) | Small libraries, few lines of code |
| TBA access | **requests** (or `tbapy`) | Simple HTTP calls |
| Scheduling | **cron** or **APScheduler** | Runs ingest and metrics automatically |
| Offline assets | HTMX, Pico.css, Plotly, and fonts saved in `web/static/vendor/` | No CDN links, so pages load with no internet |
| Offline packages | A `wheelhouse/` folder made with `pip download -r requirements.txt` | A fresh laptop can be set up with no internet |
| Hosting at events | **Primary laptop + standby laptop + dedicated router** | Works without venue internet, and survives one laptop failing |
| Hosting before events | **PythonAnywhere** or **Render** (optional) | Lets students look things up from home |
| Code sharing | **GitHub** | Pull requests, issues, code review |

### Why Flask and not something else?

- **Streamlit** is faster to start, but gives us less control over phone layouts, and it reruns the whole script on each click.
- **FastAPI + JavaScript framework** means two languages and more complexity than we need.
- **Flask + HTMX** is the sweet spot: pages are built on the server in Python, so a student who knows Python and a little HTML can contribute.

*Mentors: if the team has zero web experience, Streamlit is a reasonable choice for an analysis-only dashboard. The scan page and match prep page are still better in Flask.*

---

## 6. Data sources

**All three outside sources are optional during the event.** We load everything we can before we arrive, and treat live updates as a bonus. Here is what we need at an event and how we get it if the internet is down:

| Data | When we need it | If we are offline |
| --- | --- | --- |
| Team list, team history, awards | Before the event | Already pre-loaded by the prefetch script |
| Statbotics EPA | Before the event | Pre-loaded snapshot with a timestamp; our own metrics take over during the event |
| Match schedule | Start of qualifications | Fetch it the night before if posted; otherwise import `schedule.csv` typed from the posted schedule |
| Match results and scores | After every match | Type scores into the manual results page; scouted point totals fill the gaps |
| Rankings | Throughout | Type them in, or use our own estimate (marked as such) |
| Alliance selection | Playoffs | The **taken** button on the alliance tracker |

### The Blue Alliance (TBA) API v3: primary source

- Free; requires an API key (create one on your TBA account page).
- Provides teams, events, schedules, match results, rankings, alliances, awards, and OPR/DPR/CCWM.
- Supports **ETags**: we ask "has this changed?" and TBA answers "no" cheaply. Always use this.
- **Etiquette:** cache responses, do not poll faster than once a minute or two, and never put the API key in GitHub.

### Statbotics: second source

- Free API and a Python package.
- Provides **EPA**, an Elo-style team strength rating that is a strong predictor.
- We pull a **snapshot** before the event (this season's EPA, last season's EPA, and each team's history) and store it with a timestamp. Only the prefetch script calls Statbotics.
- Statbotics is built from the same match data we may not be able to download at the event, so it will probably be offline when we are. During the event, **our own Elo, TrueSkill, and OPR** (computed locally) are the primary ratings. We seed them from the Statbotics snapshot.

### FIRST FRC Events API: later, if needed

- The official source. Requires registration and has a clunkier data model. It can act as a \*\*second live source\*\* if TBA is slow or down on a busy competition day, and the ingest script can switch between them.
- TBA already pulls from it, so we only add it if we find gaps (for example, if TBA is slow to update).

### Our scouting data

- Comes from ScoutingPASS (see Section 8). This is our competitive advantage because nobody else has it.

---

## 7. Database design

The database is a single SQLite file (for example, `data/scouting.db`). Here are the main tables.

### Public data tables

| Table | Key columns | Notes |
| --- | --- | --- |
| `teams` | team\_number, name, city, state, rookie\_year |  |
| `events` | event\_key, name, start\_date, end\_date | Keys look like `2026nyro` |
| `event_teams` | event\_key, team\_number | Which teams attend which event |
| `matches` | match\_key, event\_key, comp\_level, match\_number, red1-3, blue1-3, red\_score, blue\_score, time | Unplayed matches have no score yet |
| `rankings` | event\_key, team\_number, rank, record, ranking\_points | Updated during the event |
| `raw_api_cache` | url, etag, response\_json, fetched\_at | Saves what TBA sent us |

### Our scouting tables

| Table | Key columns | Notes |
| --- | --- | --- |
| `raw_scans` | id, scanned\_at, raw\_text, status, error\_message | **Every scan is saved here first** |
| `match_scouting` | event\_key, match\_key, team\_number, scout, timestamp, `data` (JSON) | One row per robot per match |
| `pit_scouting` | event\_key, team\_number, scout, timestamp, `data` (JSON) | One row per team |
| `field_definitions` | field\_name, type, aggregation | Loaded from the ScoutingPASS config |

**Unique key rule:** a match scouting row is identified by `(event_key, match_key, team_number)`. Scanning the same QR code twice **updates** the row instead of creating a duplicate. This is called an *upsert*, and it makes accidental double scans harmless.

### Computed tables

| Table | Key columns | Notes |
| --- | --- | --- |
| `team_metrics` | team\_number, event\_key, metric\_name, value, source, updated\_at | One row per team per metric (opr, elo, trueskill, epa\_pre\_event, epa\_live, scouted\_avg\_cycles, ...) |
| `picklist` | event\_key, team\_number, rank, tag, notes, taken | The alliance selection list |
| `weights` | event\_key, metric\_name, weight | Adjustable weights for the pick list score |

### Where did this number come from? (`source` and `fetched_at`)

Tables that hold outside or typed-in data (`matches`, `rankings`, `team_metrics`) carry two extra columns so we always know how trustworthy a number is:

| Column | Values | Why |
| --- | --- | --- |
| `source` | `tba`, `first`, `statbotics`, `manual`, `scouted` | Official data overwrites typed-in or scouted stand-ins automatically when it arrives |
| `fetched_at` | timestamp | Feeds the "data last updated" banner on every page |

Two EPA values are stored: `epa_pre_event` (our pre-event snapshot) and `epa_live` (only updated if we get online). Pages show whichever is newer, with its timestamp.

### Why a JSON column for scouting data?

The game changes every January, and so do our scouting questions. If every question were its own column, we would redo the database each season. Instead:

- A few **fixed columns** hold what never changes (event, match, team, scout, time).
- The **`data` column** holds all game-specific answers as JSON, for example `{"auto_notes": 3, "climb": "deep", "defense_rating": 4}`.
- The **`field_definitions`** table says which fields are numbers, which are yes/no, and how to summarize each one (average, percent, max). The metrics code reads it, so most pages adapt to a new season automatically.

---

## 8. Scouting data flow (ScoutingPASS and the QR scanner)

We keep using ScoutingPASS for data collection. Our new system only **receives** its output.

### How the scanner works

Most USB and Bluetooth QR scanners act like a **keyboard**. When you scan a code, the scanner "types" the text into whatever is selected on the screen, then presses Enter. So the computer does not need special scanner software. A web page with a text box can receive the scan.

### The Scan page

The scouting lead opens the Scan page on a laptop and scans a stack of QR codes.

```
Scanner types text + Enter
        │
        ▼
Text box on the Scan page ──► Flask /scan
                                  │
          1. Save raw text to raw_scans (always)
          2. Parse the text into fields
          3. Validate (see below)
          4. Upsert into match_scouting or pit_scouting
          5. Reply "✔ Match 12, Team 254 saved" or "✖ reason"
```

**Page behavior:**

- The text box stays focused so the lead never needs to click between scans.
- Each scan gets an immediate green (saved) or red (problem) message. Immediate feedback means the scout may still be nearby to fix a bad entry.
- A list of the last 10 scans stays on screen.

### Validation checks

When a scan comes in, the server checks:

1. **Does the text parse?** All required fields are present and the right type.
2. **Is the team in that match?** Compare to the TBA lineup. This catches mistyped team numbers.
3. **Is it a duplicate?** If yes, update, but tell the user.
4. **Do the totals make sense?** After a match, compare the sum of scouted points for an alliance to TBA's official score. A big difference flags a bad entry. This is checked in a separate job, not during the scan.

### Known gotchas (test these early!)

| Problem | What to do |
| --- | --- |
| ScoutingPASS uses **Tab** as the delimiter, and a keyboard-style scanner types a Tab, which jumps focus out of the box | Use a `<textarea>`, change the delimiter in the ScoutingPASS config, or adjust the scanner settings |
| Scanner does not press Enter after a scan | Check the scanner manual; there is usually a setup barcode to change the suffix |
| Wrong characters typed (for example `;` or `\|`) | Scanner keyboard layout does not match the computer; change the scanner setting |
| Dense QR codes fail to scan | Test a full-size match form with the real scanner |
| Pit photos | QR codes cannot hold images. Store photos in a shared folder named by team number and link them from the team page |

### First task: collect a sample

Before writing any code, scan one real match QR code and one real pit QR code into a plain text editor. Save the raw text files in the repo under `tests/samples/`. These samples become the foundation for the parser and its tests.

---

## 9. Metrics

At the event, \*\*our own metrics are the primary ones\*\*. Statbotics EPA is a pre-event snapshot that is refreshed only if we get online. All metrics are calculated by scripts in `metrics/` and saved into `team_metrics`. Pages just read them.

| Metric | Where it comes from | What it tells us |
| --- | --- | --- |
| **OPR / DPR / CCWM** | TBA when online; otherwise computed by us from the matches we have | Estimated points a team contributes (offense, defense, margin) |
| **EPA** | Statbotics, as a pre-event snapshot | An Elo-style rating of team strength, strong predictor |
| **Elo** | We compute it | Rating that goes up when a team's alliance wins more than expected |
| **TrueSkill** | `trueskill` package | Like Elo, but gives each team a skill estimate **and** an uncertainty; works well for 3-team alliances |
| **Scouted averages** | Our match scouting | Average cycles, auto points, climb success rate, etc. |
| **Reliability** | Our match scouting | How often a robot breaks down or does not move |
| **Subjective ratings** | Our scouting | Driver skill and defense quality (normalized per scout) |

### Computing Elo and TrueSkill: the idea

1. Load all past matches in time order. These can be official results, typed-in results, or approximate results built from our scouted point totals.
2. Give every team a starting rating, seeded from last season's rating in the Statbotics snapshot so early-event ratings are not blank.
3. For each match, predict the winner from the ratings, then adjust ratings based on how surprising the result was.
4. Save the final ratings (and optionally the history, to draw trend charts), tagged with their `source`.

Both are a few dozen lines of Python. This is a good intermediate student project.

### Normalizing scout bias

Some scouts rate everyone a 4 out of 5, and others rate everyone a 2. Later we can adjust each scout's ratings relative to their own average. This is a stretch task, not a Phase 1 requirement.

---

## 10. The web app: pages and features

The app is **mobile-first**: design for a phone screen, and it will also work on an iPad or laptop. Use big tap targets and avoid wide tables where possible.

### Goal 1 pages: before the event

| Page | Contents |
| --- | --- |
| **Team list** | All teams at the event, sortable by each metric |
| **Team profile** | Photo, name, city, rookie year, past events and awards, metric trends, our scouting notes |
| **Event preview** | Ranked table of teams by chosen metric, with filters |
| **Our schedule** | Our matches, partners and opponents, predicted win probability |

This data barely changes, so it can be prepared the week before.

### Goal 2 pages: during the event

| Page | Contents |
| --- | --- |
| **Match prep (highest priority)** | Next match: our 3 partners and 3 opponents, each with key stats, strengths, weaknesses, and strategy notes. Designed for the drive team to read in 60 seconds |
| **Live rankings** | Current standings and ranking points |
| **Match list** | Results and upcoming matches; our matches highlighted |
| **Scan page** | For the scouting lead (Section 8) |
| **Coverage page** | A grid of matches and robots showing which are missing scouting data |
| **Data quality page** | Flagged matches where scouted totals do not match TBA |
| **Data freshness banner** | Shown on every page: when data was last updated and from what source (for example, "Match data as of 2:14 PM, from TBA" or "typed in by hand") |
| **Schedule import (admin)** | Upload `schedule.csv` (match number, red 1-3, blue 1-3) so the app runs even with no internet |
| **Manual results entry (admin)** | A form to type in red and blue scores and rankings from the venue displays; rows are saved with `source = manual` |
| **Snapshot export (admin)** | One button that saves the key pages as self-contained HTML files (see Section 11) |

Pages that need fresh data refresh themselves with HTMX, for example `hx-trigger="every 30s"`. We do **not** need websockets.

### Goal 3 pages: alliance selection

| Page | Contents |
| --- | --- |
| **Pick list builder** | All teams with a combined score; drag to reorder; tags such as *First pick*, *Second pick*, *Do not pick*, *Defense specialist* |
| **Weights panel** | Sliders for how much each metric counts (for example 40% scouted performance, 30% EPA, 20% TrueSkill, 10% reliability) |
| **Alliance tracker** | Marks teams as **taken** as alliances form, by button press or from TBA data |
| **Autosave and snapshots** | Every change is saved to the database, with a timestamped JSON copy kept on disk. A snapshot of the pick list is exported just before alliance selection starts, so we always have the last known-good ranking |

---

## 11. Connectivity and degraded modes

We assume the venue internet **will not be reliable**. The app, the data it needs, and its backup all run on our own equipment. Internet only refreshes data; it is never required.

### Degraded modes

| Situation | What still works | What we do |
| --- | --- | --- |
| **Full internet** | Everything | Ingest polls TBA (or FIRST) every 1-2 minutes |
| **Hotspot on the sync laptop only** | Everything | TBA with ETags uses very little data; one phone is enough. Other devices stay on our private router |
| **No internet, schedule loaded** | All pages, scanning, match prep, pick list | Type in scores and rankings on the manual results page; our own Elo, TrueSkill, and OPR keep updating |
| **No internet, no schedule** | Team pages, scanning, pick list | Import `schedule.csv` typed from the posted schedule |
| **Primary laptop fails** | Everything, on the standby laptop | Switch to the standby; lose at most the last sync interval |
| **Both laptops fail** | Read-only snapshots on iPads and phones | Use the snapshots and screenshots (below) while we recover |

### Equipment at the event

```
  Primary laptop (runs the app)  ◄──── copy database every 30-60 min ────►  Standby laptop (same app, same data)
          │                                                                       │
          └──────────────── Dedicated wifi router (no internet needed) ───────────┘
                                          │
                              phones and iPads (users, scouts)

  Sync laptop (can be the primary): uses a phone hotspot, only runs prefetch/ingest
```

### The hot standby laptop

- It runs the full app, including the pick list, with its **own copy** of the database.
- Copy the database file to it every 30-60 minutes, after every scanning session, and after every pick list change during alliance selection. A USB drive or the local router both work, since the database is one file.
- Test the standby the night before: start it with the wifi off and confirm the pages load.
- If the primary dies, point devices at the standby's address and keep working.

### Snapshots and screenshots

A snapshot is a **self-contained HTML file** of a page. It opens on any phone or iPad with no server running, and iPads can keep them in the Files app. Snapshots are read-only: they are for *looking*. The standby laptop is for *working*.

| When | What to save | Who |
| --- | --- | --- |
| Start of each competition day | Team list, team profiles, our schedule | Programming lead |
| Every few matches | Match prep for our next 3 matches | Strategy lead |
| End of each day | Rankings and the pick list | Strategy lead |
| Just before alliance selection | The pick list, the taken list, and the weights | Strategy lead |
| After any pick list change during selection | Screenshot of the pick list | Whoever is editing |

A screenshot of the running app counts as a snapshot when the export button is not available. Take them on a schedule, not only when something has already gone wrong.

### Manual entry tools

If TBA is unreachable, a student can keep the system alive with two admin pages:

1. **Schedule import:** upload `schedule.csv` with the match number and the red and blue teams.
2. **Manual results:** type the red and blue scores (and rankings) read from the venue displays.

Manual rows are marked `source = manual`. When official data arrives later, it automatically overwrites them. If official scores are missing, scouted point totals can stand in (marked `source = scouted`).

### Pre-load before the event

The `prefetch` script saves teams, past results, awards, the schedule (if posted), and the Statbotics snapshot into the database. Run it at home the week before and again at the hotel the night before. The app is useful even if we never get online at the venue.

### Everything must be local

- JavaScript, CSS, and fonts live in `web/static/vendor/`. No CDN links.
- Python packages are saved in `wheelhouse/` so any laptop can be set up offline.
- The web app reads only the local database.

### Night-before checklist

- [ ] Run prefetch (TBA, Statbotics, and the schedule if posted).
- [ ] Turn wifi off and confirm the app starts and every main page loads.
- [ ] Copy the database to the standby laptop and confirm the standby runs.
- [ ] Export snapshots and take screenshots of the pick list and match prep.
- [ ] Test the scanner on a real code, and test the manual score entry page.
- [ ] Charge both laptops, and pack the router, extension cords, and a USB drive.

---

## 12. Code organization

One GitHub repository with a few small folders:

```
scouting-hub/
├── README.md              # how to install and run (keep this short and current)
├── requirements.txt       # Python packages
├── wheelhouse/            # downloaded packages for offline installs (not in git)
├── run.py                 # starts the web app
├── config.py              # event key, season, settings (no secrets!)
├── .env.example           # shows which secrets are needed (TBA key); real .env is NOT in git
├── data/
│   └── scouting.db        # the database (not in git)
├── prefetch/              # before-the-event loader: TBA, Statbotics, schedule
├── ingest/                # live polling of TBA/FIRST during the event
├── scanning/              # parser, validator, importer for ScoutingPASS data
├── metrics/               # opr, elo, trueskill, scouted averages
├── exports/               # snapshot export and database copy/sync scripts
├── web/
│   ├── app.py             # Flask app
│   ├── routes/            # one file per area (teams, matches, scan, picklist, admin)
│   ├── templates/         # Jinja HTML files
│   └── static/
│       └── vendor/        # HTMX, Pico.css, Plotly, fonts saved locally (no CDN)
├── seed/                  # loads a past event so we can develop without live data
├── tests/
│   └── samples/           # real example scans and API responses
└── docs/
    └── design.md          # this document
```

### One-command setup (goal)

```
git clone <repo>
cd scouting-hub
pip install -r requirements.txt
python seed/load_past_event.py
python run.py
```

A new student should see a working website with real-looking data within 10 minutes.

---

## 13. How we work together

### Rules for contributing

1. Pick an issue on GitHub (look for the **good first issue** label).
2. Make a branch, make a small change, and open a **pull request**.
3. One other person reviews it (a student reviewer is fine; a mentor reviews anything touching the database).
4. Merge when it runs and has a short note explaining what changed.

### Working in vertical slices

Instead of a "database team" and a "web team," assign **one feature end to end**. For example: *"Team profile page"* means the SQL query, the Python route, and the HTML template. Students learn more and integration problems show up early.

### Starter tasks by experience

| Level | Example tasks |
| --- | --- |
| **Beginner** | Style a page; add a column to a table; write the README setup steps; add a new tag to the pick list; download the JavaScript and CSS files into `web/static/vendor/`; write the night-before checklist as a printable page |
| **Intermediate** | Write the Elo calculator; build the team profile page; write the QR scan parser against sample data; add tests; build the `schedule.csv` import page; build the manual results entry page; write the OPR calculation from match data |
| **Advanced** | Idempotent import logic; the scoring/weights engine for the pick list; scout-bias normalization; the validation job that compares scouted totals to TBA; the snapshot export (pages to self-contained HTML); the database sync to the standby laptop; switching between TBA and FIRST as live sources |

### Secrets and safety

- The TBA API key lives in a `.env` file that is **never** committed to GitHub.
- Use a shared **event passcode** for access to the app (simple, not fancy). Only a few people get admin access to import, delete, or edit the pick list.
- Scouting data should contain **team numbers and scout initials**, not full student names. Be careful about posting photos of students. Check school and team policies.

### Testing

- **Unit tests** (pytest) for the parser, the validator, and the metrics, using the real samples in `tests/samples/`.
- **Dress rehearsal:** before a real competition, run the whole system at an off-season event or a practice scrimmage. Break things on purpose (unplug the internet, scan a bad code) and see what happens.
- **Offline drill:** with the wifi off, import a schedule from CSV, type in a few match scores by hand, scan some codes, build a pick list, export snapshots, then "kill" the primary laptop and carry on from the standby. If the team can do this comfortably, we are ready.

---

## 14. Roadmap

Each phase delivers something usable on its own.

| Phase | What we build | Goal served | Done when... |
| --- | --- | --- | --- |
| **0. Setup** | Repo, README, seed data for a past event, real ScoutingPASS scan samples, **vendored JS/CSS/fonts, offline package folder, prefetch script** | All | A new student can run the app in 10 minutes, with the wifi off |
| **1. Public data MVP** | TBA ingest, SQLite, team list and team profile pages, OPR and EPA snapshot displayed, **data freshness banner** | 1 | We can look up any team at our next event |
| **2. Scouting import and own metrics** | Scan page, parser, validator, upsert, coverage page, scouted averages, **own Elo, TrueSkill, and OPR computed locally** | 2 | Scanned data shows up on team profiles within seconds, and ratings update with no internet |
| **2.5. Event readiness** | **Schedule CSV import, manual results entry, `source` tracking, snapshot export, standby laptop sync, offline drill** | 2 | We complete the offline drill with the primary laptop "killed" |
| **3. Live event tools** | Live polling, match list, rankings, **match prep page**, FIRST API as second live source | 2 | Drive team uses the match prep page at an event |
| **4. Alliance selection** | Pick list builder with weights, tags, taken tracker, **autosave and pre-selection snapshot** | 3 | We run alliance selection from the tool |
| **5. Stretch** | Match predictions, playoff simulation, scout-bias normalization | All | Whatever the team is excited about |

**Suggested order of attention:** if time is short, build Phase 0, Phase 1, Phase 2, Phase 2.5, and the match prep page from Phase 3. Phase 2.5 is not optional: without it, one dead wifi connection or one dead laptop stops the system at the event.

---

## 15. Risks and how we reduce them

| Risk | Why it matters | What we do |
| --- | --- | --- |
| No internet at the venue | Live data stops updating | Pre-load everything; local server + router; hotspot on one sync laptop; manual schedule and score entry |
| TBA or Statbotics unavailable | No live data or no EPA | Web app never calls them; pre-event snapshots; own metrics take over; FIRST API as a second live source |
| Primary laptop fails | App and pick list go down | Hot standby laptop with a database copy every 30-60 minutes; snapshots on iPads |
| A page needs the internet (CDN, fonts, packages) | Pages break offline | Vendor all JS/CSS/fonts locally; keep a `wheelhouse/` of packages; test with wifi off |
| Typed-in or scouted stand-in data mistaken for official data | Wrong decisions | `source` column and the data freshness banner; official data overwrites stand-ins |
| Scanner or QR quirks | Data does not import | Test the real scanner in Phase 0; save raw scans |
| Bad scouting data | Wrong picks | Validate against TBA; coverage and data-quality pages |
| Students graduate | Nobody understands the code | Keep it simple; keep README and this document current; pair students on tasks |
| Season changes the game | Forms and metrics break | JSON data column plus `field_definitions`; read from the ScoutingPASS config |
| Over-engineering | We never finish | Follow the design principles; ship Phase 1 before starting Phase 3 |
| TBA rate limits | No updates | ETags, caching, and a saved copy of the last good data |
| Leaked API key or student data | Privacy and security issues | `.env` file, initials only, shared passcode, review photo policy |

---

## 16. Open questions for the team

Please discuss and record answers here.

1. **Scanner model and output:** What scanner do we have? What exactly does a real match scan look like (delimiter, length, line ending)?
2. **Which devices run the app at events?** Which laptop is primary, which is the standby, and who owns each?
3. **Who is the scouting lead** responsible for scanning and checking the coverage page?
4. **What is the first event** we want to use this at, and what is our deadline?
5. **Hosting before events:** do we want a cloud copy for pre-event research?
6. **Photos:** how do we want to store and share pit photos?
7. **Pick list inputs:** which metrics does the strategy team trust the most? How should the starting weights be set?
8. **Mentor owner:** who is responsible for database changes and merging code?
9. **Sync laptop and hotspot:** who runs the sync laptop, and do we have hotspots on two different carriers?
10. **Snapshot schedule:** who is responsible for exporting snapshots and taking screenshots, and when?
11. **Backup copy method:** USB drive, local router, or both?

---

## 17. Glossary

| Term | Meaning |
| --- | --- |
| **API** | A way for one program to request data from another over the internet |
| **API key** | A password-like code that identifies who is using an API |
| **CCWM** | Calculated Contribution to Winning Margin (OPR minus DPR) |
| **cron / APScheduler** | Tools that run a script automatically on a schedule |
| **Degraded mode** | A way of running the system when something (usually the internet) is missing |
| **DPR** | Defensive Power Rating; how many points an alliance allows |
| **ETag** | A tag that lets us ask "has this data changed?" without downloading it again |
| **Elo** | A rating system that rises with wins against stronger opponents |
| **EPA** | Expected Points Added; Statbotics' Elo-style team rating |
| **Flask** | A small Python web framework |
| **Hot standby** | A second computer already running the same app with a recent copy of the data, ready to take over |
| **HTMX** | A small library that updates parts of a page without writing JavaScript |
| **Idempotent** | Doing the same action twice has the same result as doing it once |
| **Jinja** | The template language Flask uses to build HTML pages |
| **JSON** | A text format for structured data, such as `{"team": 254}` |
| **OPR** | Offensive Power Rating; estimated points a team adds to its alliance |
| **Prefetch** | A script that downloads and saves the data we need before the event |
| **PWA** | Progressive Web App; a website that behaves like an installed app |
| **Pull request** | A proposed code change on GitHub that others review before merging |
| **Snapshot** | A self-contained, read-only HTML copy of a page that opens without a server |
| **SQLite** | A database stored in a single file |
| **Statbotics** | A site and API that computes EPA and other FRC statistics |
| **TBA** | The Blue Alliance, a community website and API for FRC data |
| **TrueSkill** | A rating system (originally from Xbox) that tracks skill and uncertainty |
| **Upsert** | Insert a row if new; update it if it already exists |
| **Vendoring** | Saving a copy of a library's files in our own project instead of loading them from the internet |
| **Vertical slice** | One feature built through every layer: database, logic, and page |

---

## 18. Next steps (this week)

1. Create the GitHub repo and add this document as `docs/design.md`.
2. Get a TBA API key and make one successful API call from Python.
3. Scan one real match code and one real pit code into a text file; commit them to `tests/samples/`.
4. Save HTMX, Pico.css, and Plotly into `web/static/vendor/`, and confirm a page loads with the wifi off.
5. Assign owners for: ingest and prefetch, scan parser, team pages, the README, and the standby laptop and snapshot routine.
6. Hold a 30-minute kickoff where mentors and students review this document and answer the open questions in Section 16.