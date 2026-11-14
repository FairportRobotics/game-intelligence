import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_load_past_event_runs_as_script(tmp_path):
    project = tmp_path / "project"
    for relative_path in (
        "config.py",
        "db.py",
        "schema.sql",
        "seed/__init__.py",
        "seed/load_past_event.py",
    ):
        destination = project / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative_path, destination)

    result = subprocess.run(
        [sys.executable, "seed/load_past_event.py"],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Database initialized." in result.stdout
    assert (project / "data/scouting.db").exists()
