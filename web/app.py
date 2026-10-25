"""
web/app.py - Create and configure the Flask app.

PURPOSE
    `create_app()` builds the app, connects every page ("route"), and sets up
    things every page needs (the passcode check and the data freshness banner).

WHAT BELONGS HERE
    - create_app(): the app factory.
    - Registering blueprints from web/routes/ (one file per area of the site).
    - A context processor that gives every template `freshness` and `our_team`.

WHAT DOES NOT BELONG HERE
    - Page logic. Put it in web/routes/<area>.py.
    - Database queries that are specific to one page.

HOW TO ADD A NEW PAGE
    1. Add a function with @bp.route("/your-url") to a file in web/routes/
       (or make a new file and register it below).
    2. Add an HTML file in web/templates/ that starts with
       {% extends "base.html" %}.
    3. Add a link to it in web/templates/base.html.

LEVEL: Beginner to Intermediate.
"""

from flask import Flask

import config
import db
from web import auth
from web.routes import admin, matches, picklist, scan, teams


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    # Passcode check for every page (see web/auth.py)
    auth.init_auth(app)

    # Pages
    app.register_blueprint(teams.bp)
    app.register_blueprint(matches.bp)
    app.register_blueprint(scan.bp)
    app.register_blueprint(picklist.bp)
    app.register_blueprint(admin.bp)

    @app.context_processor
    def inject_globals():
        """Values available in EVERY template."""
        return {
            "freshness": db.data_freshness(),   # for the "data last updated" banner
            "our_team": config.OUR_TEAM,
            "event_key": config.EVENT_KEY,
            "refresh_seconds": config.PAGE_REFRESH_SECONDS,
        }

    return app
