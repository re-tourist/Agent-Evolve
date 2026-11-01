"""Capture allowlisted environment metadata; never read secrets or overwrite output."""

import argparse
import datetime
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def snapshot() -> dict:
    packages = {}
    for name in ("agent-evolve", "pytest", "ruff"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "created_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "python": platform.python_version(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "git_commit": git_commit(),
        "packages": packages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="runs/metadata/environment.json")
    out = Path(parser.parse_args().output)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with out.open("x", encoding="utf-8") as stream:
            json.dump(snapshot(), stream, indent=2)
            stream.write("\n")
    except FileExistsError:
        raise SystemExit("Refusing to overwrite existing environment snapshot") from None
    print("Environment snapshot written")


if __name__ == "__main__":
    main()
