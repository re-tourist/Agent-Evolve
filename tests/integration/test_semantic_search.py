"""Real pinned GEPA custom sampling and feedback consumption; synthetic scores only."""

import json
import os
from pathlib import Path

import pytest

from agent_evolve.baseline import deny_network, write_json
from agent_evolve.gepa_adapter import TaskSets
from agent_evolve.live_runtime import Budget
from agent_evolve.optimization import optimize_live
from agent_evolve.study import FailureSampler

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_GEPA_TESTS") != "1", reason="pinned GEPA"
)


def test_multiple_proposals_use_actual_failure_feedback(tmp_path):
    class Client:
        directory = tmp_path
        config = {
            "study": "synthetic",
            "search": {"max_evals": 30, "minibatch": 3, "max_proposals": 4},
        }
        budget = Budget.create(
            tmp_path / "budget.json",
            limit=5000,
            cost_limit_rmb=50,
            phase_limits={"structured": 5000},
            task_calls=48,
        )
        n = 0

        def sampler(self, phase):
            return FailureSampler(
                {str(i): {"reward": i % 2} for i in range(6)}, 3, tmp_path / "samples.jsonl"
            )

        def semantic_feedback(self, result, prompt, directory, example):
            return {"diagnostics": [{"suggestion": "SYNTHETIC_EVIDENCE_MARKER"}]}

        def execute(self, job):
            self.n += 1
            assert "SYNTHETIC_EVIDENCE_MARKER" in str(job["messages"])
            if self.n == 1:
                assert "official_reward\n0.0" in str(job["messages"])
            p = Path(job["directory"])
            p.mkdir()
            write_json(p / "output.json", {"text": f"synthetic instruction {self.n}"})

        def task(self, candidate, task_id, phase, directory):
            score = 0.0 if candidate == "seed" else 0.5
            result = {
                "messages": [],
                "termination_reason": "user_stop",
                "official_task_reward": score,
                "excluded_from_task_metrics": False,
            }
            return (
                score,
                {
                    "task_id": task_id,
                    "official_reward": score,
                    "status": "fixture",
                    "termination_reason": "user_stop",
                },
                result,
                {"policy_sha256": "fixed"},
                {},
            )

    with deny_network():
        result = optimize_live(
            Client(),
            "structured",
            "seed",
            TaskSets(tuple(map(str, range(6))), ("8", "10"), ("12",)),
        )
    assert result["summary"]["new_candidates_evaluated"] >= 2
    assert len(result["summary"]["train_tasks_observed"]) >= 3
    assert result["summary"]["best_complete_validation"]
    pool = json.loads((tmp_path / "structured/candidate_pool.json").read_text())
    assert len(pool) >= 2
