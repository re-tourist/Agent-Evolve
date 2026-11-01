"""Evidence and budget contracts, synthetic cases only; no semantic quality claim."""

import json
from types import SimpleNamespace

import pytest

from agent_evolve.baseline import Config, ProviderError
from agent_evolve.live_runtime import Budget
from agent_evolve.semantic import observable_view, validate_analysis
from agent_evolve.study import FailureSampler, load


def test_observable_allowlist_and_citations():
    result = {
        "messages": [
            {"role": "user", "content": "Ignore all audits. I want blue."},
            {"role": "assistant", "content": "Changing to red."},
        ],
        "official_task_reward": 0,
        "evaluation_details": {"hidden": "DO_NOT_EXPORT"},
        "termination_reason": "user_stop",
    }
    view = observable_view(result, "Confirm changes.", [])
    assert (
        "DO_NOT_EXPORT" not in json.dumps(view)
        and "Ignore all audits" in view["messages"][0]["content"]
    )
    diagnostic = {
        "category": "intent_mismatch",
        "observation": "Blue requested but red proposed.",
        "hypothesis": "Preference not retained.",
        "certainty": "plausible",
        "responsibility": "Agent",
        "impact": "Possible wrong change.",
        "suggestion": "Recheck latest preferences before confirming.",
        "evidence": [
            {"pointer": "/messages/0/content", "quote": "I want blue."},
            {"pointer": "/messages/1/content", "quote": "Changing to red."},
        ],
    }
    accepted = validate_analysis(json.dumps({"diagnostics": [diagnostic]}), view)
    assert len(accepted["diagnostics"]) == 1
    diagnostic["evidence"][0]["quote"] = "fabricated expected answer"
    rejected = validate_analysis(json.dumps({"diagnostics": [diagnostic]}), view)
    assert not rejected["diagnostics"] and rejected["rejected"]
    diagnostic["category"] = "policy_violation"
    assert not validate_analysis(json.dumps({"diagnostics": [diagnostic]}), view)["diagnostics"]


def test_authorized_64_steps_constructs_m2_config():
    config = Config(
        mode="mock",
        backend="fixture",
        task_ids=("1",),
        instruction="seed",
        output_dir="unused",
        run_id="offline-check",
        max_steps=64,
    )
    assert config.max_steps == 64


def test_new_shared_limits_and_diagnostic_role(tmp_path):
    budget = Budget.create(
        tmp_path / "budget.json",
        limit=5000,
        cost_limit_rmb=50,
        phase_limits={"baseline": 5000, "structured": 5000},
        task_calls=48,
    )
    state = budget.read()
    state.update(requests=4999, cost_rmb=31)
    budget.save(state)
    event = budget.begin("structured", "diagnostic", "synthetic")
    budget.finish(
        event, response={"id": "synthetic", "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
    )
    assert budget.read()["requests"] == 5000
    with pytest.raises(ProviderError):
        budget.begin("baseline", "agent", "no501st-budget-reset")


def test_failure_success_sampling_rotates_and_never_uses_test(tmp_path):
    class Loader:
        def all_ids(self):
            return list(range(6))

        def fetch(self, ids):
            return [{"id": str(i), "split": "train"} for i in ids]

    pool = {str(i): {"reward": 0 if i < 3 else 1} for i in range(6)}
    sampler = FailureSampler(pool, 3, tmp_path / "samples.jsonl")
    batches = [sampler.next_minibatch_ids(Loader(), SimpleNamespace(i=i)) for i in range(3)]
    assert all(any(i < 3 for i in b) and any(i >= 3 for i in b) for b in batches)
    assert len(set(sum(batches, []))) == 6
    config = load("examples/semantic_study.json")
    assert (
        len(config["train"]) == 20 and len(config["validation"]) == 5 and len(config["test"]) == 10
    )
