"""
scanning/parser.py - Split one scanned QR string into named fields.

PURPOSE
    A scanner "types" the QR text. This file turns that raw text into a Python
    dict like:
        {"form": "match", "event_key": "2026nyro", "match_number": 12,
         "team_number": 254, "scout": "AB", "data": {"auto_notes": 3, ...}}

START HERE (before writing any code!)
    1. Scan one real match code and one real pit code into a plain text editor.
    2. Save the raw text in tests/samples/ (e.g. match_scan_1.txt).
    3. Look at the delimiter (tab? semicolon? comma?), the field order, and any
       line endings. Write the parser to match the REAL sample.
    4. Write tests in tests/test_parser.py using those samples FIRST.

WHAT SHOULD BE IN THIS FILE
    - parse_scan(raw_text): return a dict as shown above, or raise ValueError
      with a short, human-readable reason ("Expected 24 fields, got 22").
    - Detect whether the scan is a match form or a pit form.
    - Convert numbers to int/float and yes/no to True/False using the field
      definitions from scanning/config_loader.py.
    - Strip whitespace and line endings the scanner added.

GOTCHAS (see Section 8 of the design doc)
    - If ScoutingPASS uses TAB as the delimiter, a keyboard-style scanner types
      a Tab key, which can move focus away from the text box. The scan page uses
      a <textarea> for this reason.
    - Never trust the input. Wrong length, missing fields, and weird characters
      are normal. Raise ValueError, do not crash.

LEVEL: Intermediate.
"""


def parse_scan(raw_text: str) -> dict:
    """
    Parse one scan into a dict of named fields.

    TODO (Intermediate): implement against tests/samples/ once real scans exist.
    """
    raise NotImplementedError("TODO: write the parser against a real sample scan")
