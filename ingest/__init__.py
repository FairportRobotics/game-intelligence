"""ingest/ - Live data polling during the event (TBA, and later FIRST).

These scripts are the ONLY place (besides prefetch/) that talk to outside APIs.
The web app never does. If the internet is down, ingest must fail quietly,
log it, and try again later.
"""
