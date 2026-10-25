"""
web/routes/teams.py - Team list and team profile pages. (Goal 1: before the event)

PAGES
    /              Home page (links to everything)
    /teams         All teams at the event, sortable by each metric
    /teams/<n>     One team's profile

WHAT THE TEAM LIST SHOULD SHOW
    Team number, name, and one column per metric from `team_metrics`
    (opr, elo, trueskill, epa, scouted averages). Click a column header to sort.

WHAT THE TEAM PROFILE SHOULD SHOW
    - Name, city, rookie year, robot photo (a file in a shared folder named by
      team number)
    - Metrics, with their `source` and `updated_at`
    - Pit scouting answers (from `pit_scouting.data` JSON)
    - Match-by-match scouting (from `match_scouting`)
    - (Stretch) Trend chart of Elo/TrueSkill over the event using Plotly

GOOD FIRST TASKS
    Beginner: style the table, add a column.  Intermediate: the profile page.

LEVEL: Beginner to Intermediate.
"""

from flask import Blueprint, render_template

import config
import db

bp = Blueprint("teams", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/teams")
def team_list():
    # TODO (Beginner): also join `team_metrics` so each row shows metrics.
    rows = db.query_all(
        """
        SELECT t.team_number, t.name, t.city
        FROM event_teams et
        JOIN teams t ON t.team_number = et.team_number
        WHERE et.event_key = ?
        ORDER BY t.team_number
        """,
        (config.EVENT_KEY,),
    )
    return render_template("teams_list.html", teams=rows)


@bp.route("/teams/<int:team_number>")
def team_profile(team_number: int):
    # TODO (Intermediate): load metrics, pit scouting, and match scouting for this team.
    team = db.query_one("SELECT * FROM teams WHERE team_number = ?", (team_number,))
    return render_template("team_profile.html", team=team, team_number=team_number)
