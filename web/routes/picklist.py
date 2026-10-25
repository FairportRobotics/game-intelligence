"""
web/routes/picklist.py - The pick list and alliance tracker. (Goal 3)

PAGES
    GET  /picklist                 Ranked list with combined score, tags, and notes
    POST /picklist/reorder         Save a new order after drag-and-drop
    POST /picklist/tag             Set a tag: first_pick, second_pick, do_not_pick, defense
    POST /picklist/taken           Mark a team as taken (on an alliance)
    POST /picklist/weights         Save the metric weights from the sliders

HOW THE COMBINED SCORE WORKS
    score = sum(weight[metric] * normalized_value[team][metric])
    Example weights: scouted performance 40%, EPA 30%, TrueSkill 20%, reliability 10%.
    Normalize each metric to 0-1 first so different units can be compared.
    Put the calculation in its own function (try metrics/ or a helper here) so it
    can be tested.

SAFETY RULES (alliance selection is high pressure!)
    - Save EVERY change to the database immediately.
    - Also write a timestamped JSON copy to config.PICKLIST_AUTOSAVE_DIR so a
      crashed browser or laptop loses nothing.
    - Exporting a snapshot just before selection starts is part of our checklist.

SortableJS (a small drag-and-drop library) goes in web/static/vendor/.

LEVEL: Intermediate (list, tags) / Advanced (weights engine, autosave).
"""

from flask import Blueprint, render_template

bp = Blueprint("picklist", __name__)


@bp.route("/picklist")
def picklist():
    # TODO (Intermediate): load `picklist` joined with metrics; compute the combined score.
    return render_template("picklist.html", teams=[])
