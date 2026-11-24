# Single-writer SQLite event handoff

The app must remain usable without internet and uses SQLite, so each competition has one writable event database hosted on the event network; after the event, that copy is verified and promoted to the canonical team database with a backup. This avoids silently merging concurrent SQLite copies, at the cost of a deliberate handoff between events.
