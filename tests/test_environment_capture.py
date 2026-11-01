"""Check secret exclusion and preservation of existing run evidence."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "capture_environment.py"


def test_capture_excludes_secrets_and_refuses_overwrite(tmp_path, monkeypatch):
    sentinel = "m1-test-secret-never-export"
    monkeypatch.setenv("OPENAI_API_KEY", sentinel)
    output = tmp_path / "environment.json"
    command = [sys.executable, str(SCRIPT), "--output", str(output)]
    first = subprocess.run(command, capture_output=True, text=True, check=False)
    assert first.returncode == 0, first.stderr
    original = output.read_bytes()
    payload = json.loads(original)
    assert set(payload) == {
        "created_utc",
        "python",
        "system",
        "release",
        "machine",
        "git_commit",
        "packages",
    }
    assert sentinel not in original.decode() + first.stdout + first.stderr
    second = subprocess.run(command, capture_output=True, text=True, check=False)
    assert second.returncode != 0
    assert "Refusing to overwrite" in second.stderr
    assert output.read_bytes() == original
