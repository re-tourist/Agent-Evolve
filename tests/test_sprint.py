"""Budget/split/score contracts with no SDK or model calls."""

from pathlib import Path

import pytest

from agent_evolve.baseline import TAU_SHA, ProviderError, digest, write_json
from agent_evolve.experiment import LiveEvaluator, WorkerClient, load_config, run_sprint
from agent_evolve.gepa_adapter import CandidateLedger, TaskSets
from agent_evolve.live_runtime import Budget, StageBudget, estimate_rmb


@pytest.fixture
def budget(tmp_path):
    return Budget.create(tmp_path / "budget.json")


def reply(**values):
    return {"id": "test", "usage": {"prompt_tokens": 10, "completion_tokens": 5, **values}}


def test_three_roles_count_across_phases_without_reset(budget):
    for phase, role in [("basic", "agent"), ("structured", "simulator"), ("test", "reflection")]:
        event = budget.begin(phase, role, "fixture")
        budget.finish(event, response=reply())
    state = Budget(budget.path).read()
    assert state["requests"] == 3 and state["input_tokens"] == 30
    assert state["phases"] == {"basic": 1, "structured": 1, "test": 1}
    assert state["cost_rmb"] == pytest.approx(3 * estimate_rmb(10, 5))


def test_401st_request_refused_and_attempt_logged_before_transport(budget):
    state = budget.read()
    state["requests"] = 399
    budget.save(state)
    event = budget.begin("test", "agent", "last")
    assert budget.read()["requests"] == 400 and budget.read()["pending"] == event
    budget.finish(event, response=reply())
    with pytest.raises(ProviderError):
        budget.begin("test", "agent", "never sent")
    assert budget.read()["requests"] == 400


def test_fee_threshold_stops_next_request_not_claimed_hard_bill_cap(budget):
    state = budget.read()
    state["cost_rmb"] = 29.99
    budget.save(state)
    event = budget.begin("basic", "reflection", "fixture")
    budget.finish(event, response=reply(prompt_tokens=20000))
    assert budget.read()["cost_rmb"] > 30
    with pytest.raises(ProviderError):
        budget.begin("structured", "agent", "blocked")


@pytest.mark.parametrize("usage", [None, {}, {"prompt_tokens": -1}, {"prompt_tokens": True}])
def test_missing_or_bad_usage_stops_all_phases(budget, usage):
    event = budget.begin("basic", "agent", "fixture")
    with pytest.raises(ProviderError):
        budget.finish(event, response={"usage": usage})
    assert budget.read()["requests"] == 1 and budget.read()["pending"] is None
    with pytest.raises(ProviderError):
        budget.begin("test", "simulator", "blocked")


def test_error_pending_and_stage_reserve_guards(budget):
    event = budget.begin("basic", "agent", "fixture")
    with pytest.raises(ProviderError):
        budget.admit_task("test")
    with pytest.raises(ProviderError):
        budget.finish(event, error="AuthenticationError")
    assert budget.read()["stopped"] == "AuthenticationError"


def test_test_reserve_not_spent_by_search(budget):
    state = budget.read()
    state["phases"]["basic"] = 69
    budget.save(state)
    with pytest.raises(StageBudget):
        budget.admit_task("basic")
    budget.admit_task("structured")
    budget.admit_task("test")


def test_price_tiers_and_config_are_frozen():
    assert estimate_rmb(128000, 1000) == pytest.approx(0.1044)
    assert estimate_rmb(128001, 1000) == pytest.approx(0.3272024)
    config = load_config("examples/core_experiment.json")
    assert run_sprint(config)["real_calls"] == 0


@pytest.mark.parametrize("reason", ["user_stop", "max_steps", "agent_error"])
def test_raw_official_zero_is_not_filtered_by_smoke_annotation(tmp_path, reason):
    budget = Budget.create(tmp_path / "budget.json")
    client = WorkerClient({"tau_python": "unused"}, tmp_path)

    def fake(job):
        path = Path(job["directory"]) / "task"
        path.mkdir(parents=True)
        write_json(
            path / "1.json",
            {
                "task_id": "1",
                "prompt_sha256": digest("seed"),
                "messages": [],
                "status": "step_limit",
                "official_task_reward": None,
                "excluded_from_task_metrics": True,
                "termination_reason": reason,
            },
        )
        write_json(path / "1.raw.json", {"reward_info": {"reward": 0.0}})
        write_json(
            path / "prompt.json", {"instruction_sha256": digest("seed"), "policy_sha256": "fixed"}
        )
        write_json(
            path / "metadata.json",
            {"upstream_sha": TAU_SHA, "tools_sha256": "fixed-tools", "data_identity": "fixture"},
        )

    client.execute = fake
    score, _, result, _, _ = client.task("seed", "1", "basic", tmp_path / "evaluation")
    assert score == 0 and result["excluded_from_task_metrics"] is False
    assert budget.read()["requests"] == 0  # fixture, not a paid evaluation


def test_test_rejected_before_worker_and_hidden_details_omitted(tmp_path):
    ledger = CandidateLedger(tmp_path)

    class Client:
        def task(self, *args):
            raise AssertionError("No test worker may be launched by GEPA")

    evaluator = LiveEvaluator(Client(), "structured", ledger, TaskSets(("1",), ("8",), ("5",)))
    with pytest.raises(ValueError):
        evaluator("seed", {"id": "5", "split": "test"})
    assert ledger.attempts == 0
