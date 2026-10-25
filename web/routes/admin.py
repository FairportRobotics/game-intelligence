"""
web/routes/admin.py - Admin pages for keeping the system alive without internet.

PAGES
    GET        /admin                    Menu of admin tools
    GET/POST   /admin/schedule           Import schedule.csv (match, red1-3, blue1-3)
    GET/POST   /admin/results            Type in match scores and rankings by hand
    POST       /admin/snapshot           Run exports.snapshot.save_all()
    POST       /admin/backup             Run exports.db_sync.backup_database()

WHY THESE EXIST
    If TBA is unreachable, a student can still load the schedule and type in
    scores from the venue displays. Those rows are saved with source='manual'
    and are automatically replaced when official data arrives.

RULES
    - Protect every page with web.auth.admin_required().
    - Always set `source` and `fetched_at` on rows you write.
    - Show a clear success or error message after every action.

schedule.csv FORMAT (see seed/schedule_example.csv)
    match_number,red1,red2,red3,blue1,blue2,blue3

LEVEL: Intermediate.
"""

from flask import Blueprint, render_template

bp = Blueprint("admin", __name__)


@bp.route("/admin")
def admin_home():
    return render_template("admin.html")


@bp.route("/admin/schedule", methods=["GET", "POST"])
def schedule_import():
    # TODO (Intermediate): on POST, read the uploaded CSV, validate each row, and upsert into `matches`.
    return render_template("admin_schedule.html")


@bp.route("/admin/results", methods=["GET", "POST"])
def manual_results():
    # TODO (Intermediate): on POST, save red/blue scores to `matches` with source='manual'.
    return render_template("admin_results.html")
