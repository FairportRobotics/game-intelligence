"""
scanning/config_loader.py - Read the ScoutingPASS config JSON for this season.

PURPOSE
    The ScoutingPASS config file lists every question on the match and pit forms
    (field names, types, choices). It is the single source of truth for field
    names, so our code READS it instead of hard-coding fields.

WHAT SHOULD BE IN THIS FILE
    - load_config(path): read the ScoutingPASS config JSON (ask the scouting lead
      for the current season's file; save a copy under seed/ or tests/samples/).
    - load_field_definitions(path): turn it into rows for the `field_definitions`
      table: field_name, form ('match' or 'pit'), type (number/bool/text/choice),
      and a default aggregation (number -> avg, bool -> pct, text -> none).
    - get_field_order(form): the order of fields in the QR text, which the parser
      needs to split a scan into named values.

WHY IT MATTERS
    The game changes every January. If the importer and the metrics read the
    config, most of our code keeps working with no edits.

LEVEL: Intermediate.
"""


def load_config(path: str) -> dict:
    """TODO (Intermediate): read and return the ScoutingPASS config as a dict."""
    raise NotImplementedError


def load_field_definitions(path: str) -> list[dict]:
    """TODO (Intermediate): return field definitions ready to save in `field_definitions`."""
    raise NotImplementedError


def get_field_order(form: str) -> list[str]:
    """TODO (Intermediate): return the field names in QR order for 'match' or 'pit'."""
    raise NotImplementedError
