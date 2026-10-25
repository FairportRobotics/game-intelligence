"""
web/routes/matches.py - Match list, match prep, and rankings. (Goal 2: during the event)

PAGES
    /matches        Results and upcoming matches; our matches highlighted
    /matches/prep   MATCH PREP for our next match  <- the highest-value page!
    /rankings       Live standings and ranking points

MATCH PREP PAGE (read this one carefully)
    The drive team must understand it in 60 seconds. For our next match show:
      - match number and time
      - our 3 alliance partners and 3 opponents
      - for each team: key metrics (Elo/TrueSkill/EPA/OPR), scouted strengths and
        weaknesses, reliability, and notes
      - a short "strategy" text box (saved in the database)
    Big text. Phone-friendly. Auto-refresh every config.PAGE_REFRESH_SECONDS with
    HTMX (see base.html and the hx-trigger attribute).

LEVEL: Intermediate.
"""

from flask import Blueprint, render_template

import config
import db

bp = Blueprint("matches", __name__)


@bp.route("/matches")
def match_list():
    # TODO (Beginner): highlight rows that include config.OUR_TEAM.
    rows = db.query_all(
        "SELECT * FROM matches WHERE event_key = ? ORDER BY comp_level, match_number",
        (config.EVENT_KEY,),
    )
    return render_template("matches.html", matches=rows)


@bp.route("/matches/prep")
def match_prep():
    # TODO (Intermediate): find our next unplayed match, then gather the three
    # partners and three opponents with their metrics and scouting.
    return render_template("match_prep.html")


@bp.route("/rankings")
def rankings():
    # TODO (Beginner): query `rankings` joined with `teams`, ordered by rank.
    return render_template("rankings.html", rankings=[])
