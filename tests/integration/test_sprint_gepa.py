"""Pinned engine with synthetic worker scores. No real API or performance claim."""

import json
import os
from pathlib import Path

import pytest

from agent_evolve.baseline import deny_network, write_json
from agent_evolve.gepa_adapter import TaskSets
from agent_evolve.live_runtime import Budget
from agent_evolve.optimization import optimize_live

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_GEPA_TESTS") != "1", reason="pinned GEPA only"
)


@pytest.mark.parametrize("phase", ["basic", "structured"])
def test_live_search_contract_with_synthetic_worker(tmp_path, phase):
    class Client:
        directory = tmp_path
        budget = Budget.create(tmp_path / "budget.json")

        def execute(self, job):
            assert job["kind"] == "reflection"
            directory = Path(job["directory"])
            directory.mkdir()
            assert '"split": "test"' not in json.dumps(job)
            write_json(
                directory / "output.json", {"text": "new instruction from synthetic provider"}
            )

        def task(self, candidate, task_id, phase, directory):
            assert task_id in {"1", "6", "7", "8", "10"}
            score = 0.0 if candidate == "seed" else 1.0
            result = {
                "messages": [],
                "termination_reason": "user_stop",
                "official_task_reward": score,
                "excluded_from_task_metrics": False,
            }
            return (
                score,
                {"kind": "synthetic score", "task_id": task_id},
                result,
                {"policy_sha256": "fixed"},
                {},
            )

    with deny_network():
        result = optimize_live(
            Client(), phase, "seed", TaskSets(("1", "6", "7"), ("8", "10"), ("5", "9", "12"))
        )
    assert result["summary"]["new_candidates_evaluated"] == 1
    assert result["summary"]["evaluations"] == 6
    assert result["best"] == "new instruction from synthetic provider"
    records = [
        json.loads(s) for s in (tmp_path / phase / "evaluations.jsonl").read_text().splitlines()
    ]
    assert all(("structured_feedback" in r["feedback"]) == (phase == "structured") for r in records)
