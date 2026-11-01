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
@pytest.mark.parametrize("reviewed", [False, True])
def test_live_search_contract_with_synthetic_worker(tmp_path, phase, reviewed):
    class Client:
        directory = tmp_path
        config = (
            {
                "tau_protocol": "reviewed-en-text",
                "seed": 42,
                "search": {"max_evals": 20, "minibatch": 1, "max_proposals": 1},
            }
            if reviewed
            else {}
        )
        trial_seed = 42
        budget = Budget.create(
            tmp_path / "budget.json",
            limit=5000,
            cost_limit_rmb=50,
            phase_limits={"basic": 5000, "structured": 5000},
        )
        validation_seeds = []

        def reflection_episodes(self, messages):
            return messages

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
            if task_id in {"8", "10"}:
                self.validation_seeds.append((candidate, task_id, self.trial_seed))
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

    client = Client()
    with deny_network():
        result = optimize_live(
            client, phase, "seed", TaskSets(("1", "6", "7"), ("8", "10"), ("5", "9", "12"))
        )
    assert result["summary"]["new_candidates_evaluated"] == 1
    assert result["summary"]["evaluations"] == (10 if reviewed else 6)
    if reviewed:
        for candidate in {"seed", "new instruction from synthetic provider"}:
            for task_id in {"8", "10"}:
                assert {
                    s for c, t, s in client.validation_seeds if c == candidate and t == task_id
                } == {42, 43}
    assert result["best"] == "new instruction from synthetic provider"
    records = [
        json.loads(s) for s in (tmp_path / phase / "evaluations.jsonl").read_text().splitlines()
    ]
    assert all(("structured_feedback" in r["feedback"]) == (phase == "structured") for r in records)
