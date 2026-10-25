"""
web/routes/scan.py - The Scan page for the QR-code scanner.

HOW THE SCANNER WORKS
    A USB/Bluetooth scanner acts like a KEYBOARD. When it scans a code it "types"
    the text into whatever box is selected and presses Enter. So we just need a
    page with a text box that is always selected.

PAGES
    GET  /scan            The scan page (big text box, list of recent scans)
    POST /scan            Receives one scan, calls scanning.importer.import_scan(),
                          returns a one-line result ("✔ Match 12, Team 254" or
                          "✖ reason") that HTMX puts into the page
    GET  /scan/coverage   Grid of matches x robots showing which are missing scouting
    GET  /scan/quality    Matches where scouted totals do not match official scores

PAGE BEHAVIOR (in templates/scan.html)
    - The box stays focused after every scan.
    - Green/red message for each scan. A list of the last 10 scans.
    - Use a <textarea>, not <input>, because a Tab character in the QR text would
      move focus out of an <input>.

LEVEL: Intermediate (scan page) / Advanced (coverage and quality pages).
"""

from flask import Blueprint, render_template, request

bp = Blueprint("scan", __name__)


@bp.route("/scan", methods=["GET"])
def scan_page():
    return render_template("scan.html")


@bp.route("/scan", methods=["POST"])
def scan_submit():
    raw = request.form.get("payload", "").strip()
    # TODO (Intermediate): call scanning.importer.import_scan(raw) inside try/except
    # ValueError and return the message. Use scan_result.html for the response.
    return render_template(
        "scan_result.html", ok=False, message="TODO: importer not connected yet"
    )


@bp.route("/scan/coverage")
def coverage():
    # TODO (Advanced): for each match and each of the 6 robots, is there a row in
    # match_scouting? Show a grid with missing cells in red.
    return render_template("coverage.html")


@bp.route("/scan/quality")
def quality():
    # TODO (Advanced): call scanning.validator.check_totals() for played matches.
    return render_template("quality.html")
