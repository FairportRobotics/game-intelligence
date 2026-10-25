"""
tests/test_smoke.py - Quick checks that the app starts and the main pages load.
Keep this passing at all times. Run with:  pytest
"""

import config
import db
from web.app import create_app


def make_client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()
    client.post("/login", data={"passcode": config.EVENT_PASSCODE})
    return client


def test_pages_load(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    for url in ["/", "/teams", "/matches", "/matches/prep", "/rankings",
                "/scan", "/picklist", "/admin", "/admin/schedule", "/admin/results"]:
        assert client.get(url).status_code == 200, url


def test_login_required(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    client = create_app().test_client()
    assert client.get("/teams").status_code == 302   # redirected to /login
