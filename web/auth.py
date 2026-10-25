"""
web/auth.py - A very simple shared-passcode login.

PURPOSE
    Keep random people on the venue wifi out of our scouting data. This is NOT
    real security; it is a shared event passcode (config.EVENT_PASSCODE).

WHAT SHOULD BE IN THIS FILE
    - init_auth(app): require the passcode for every page except /login and
      static files.
    - /login page: one box for the passcode; remember it in the browser session.
    - admin_required(): (TODO) a stricter check for admin pages such as import,
      delete, and manual score entry. Only a few people should have it.

TODO (Beginner): add a separate ADMIN_PASSCODE to config.py and .env.example and
use it in admin_required().

LEVEL: Beginner.
"""

from flask import redirect, render_template, request, session, url_for

import config


def init_auth(app) -> None:
    @app.before_request
    def require_login():
        if request.endpoint in ("login", "static"):
            return None
        if not session.get("ok"):
            return redirect(url_for("login"))
        return None

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            if request.form.get("passcode") == config.EVENT_PASSCODE:
                session["ok"] = True
                return redirect(url_for("teams.index"))
            error = "Wrong passcode. Ask the scouting lead."
        return render_template("login.html", error=error)


def admin_required():
    """TODO (Beginner): return a redirect/403 unless this user has admin rights."""
    return None
