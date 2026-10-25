"""
ingest/poll_event.py - Keep the database up to date during the event.

USAGE
    python -m ingest.poll_event          # runs forever, polling every ~90 seconds

PURPOSE
    Every POLL_INTERVAL_SECONDS: ask TBA (or FIRST) for new match results and
    rankings, save them in the database, then tell metrics/ to recalculate.

WHAT SHOULD BE IN THIS FILE
    - poll_once(): one pass of:
        1. fetch matches + rankings (tba_client; fall back to first_client)
        2. UPSERT into `matches` and `rankings` with source='tba' and fetched_at=now
           (official data OVERWRITES rows whose source is 'manual' or 'scouted')
        3. call metrics.run_all.run() if anything changed
    - main(): loop forever (or use APScheduler) and call poll_once().

RULES
    - If the internet is down, log one short line ("TBA unreachable, will retry")
      and keep going. Never crash, never print a huge traceback every 90 seconds.
    - Never delete data just because an API returned nothing.

LEVEL: Intermediate to Advanced.
"""

import logging
import time

import config

log = logging.getLogger(__name__)


def poll_once() -> bool:
    """
    Do one polling pass. Return True if any data changed.

    TODO (Intermediate): implement using ingest.tba_client and db.
    """
    raise NotImplementedError("TODO: fetch matches/rankings and upsert them")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            poll_once()
        except Exception as exc:  # keep running no matter what
            log.warning("Poll failed (%s). Will retry.", exc)
        time.sleep(config.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
