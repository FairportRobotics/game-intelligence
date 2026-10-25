"""
exports/snapshot.py - Save web pages as self-contained HTML files.

USAGE
    python -m exports.snapshot            # save all key pages
    (also triggered by the "Snapshot export" button on the admin page)

PURPOSE
    A snapshot opens on any phone or iPad with NO server running. It is the
    backup for when both laptops are down. Snapshots are read-only (for looking);
    the standby laptop is for working.

WHAT SHOULD BE IN THIS FILE
    - save_all(): save each key page into config.SNAPSHOT_DIR with a timestamp in
      the file name (for example picklist_2026-03-14_1415.html):
        * team list and team profile pages
        * our schedule
        * match prep for our next ~3 matches
        * rankings
        * the pick list (with the taken list and weights)
    - HOW: use Flask's test client (`app.test_client().get("/teams")`) to get the
      page HTML, then make it self-contained:
        * inline the CSS (and any small JS) into the file
        * add the "snapshot taken at <time>" note at the top
      A page that links to files in web/static/vendor/ can be inlined by reading
      those files from disk.

TIP: Do the simplest page first (team list), then add pages one at a time.

LEVEL: Advanced.
"""

import config  # noqa: F401


def save_all() -> list[str]:
    """TODO (Advanced): save every key page. Return the list of files written."""
    raise NotImplementedError
