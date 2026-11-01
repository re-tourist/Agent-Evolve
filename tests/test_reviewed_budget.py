"""Cumulative authorization cannot be reset by protocol/Run ID changes."""

import pytest

from agent_evolve.live_runtime import Budget


def test_one_successor_inherits_usage_cost_and_keeps_predecessor_stop(tmp_path):
    old = Budget.create(
        tmp_path / "old.json", limit=5000, cost_limit_rmb=50, phase_limits={"basic": 5000}
    )
    state = old.read()
    state.update(
        requests=755,
        cost_rmb=13.1905564,
        input_tokens=4002363,
        output_tokens=96029,
        stopped="InternalServerError",
        unknown_usage_requests=2,
        unknown_cost_reserve_rmb=9.796608,
    )
    old.save(state)
    original = old.path.read_bytes()
    new = Budget.carry_forward(tmp_path / "new.json", old.path, phase_limits={"structured": 5000})
    assert old.path.read_bytes() == original and old.read()["stopped"]
    assert new.read()["requests"] == 755 and new.read()["cost_rmb"] == 13.1905564
    assert new.read()["unknown_usage_requests"] == 2
    assert new.begin("structured", "reflection", "fixture")["request"] == 756
    with pytest.raises(FileExistsError):
        Budget.carry_forward(tmp_path / "another.json", old.path, phase_limits={"structured": 5000})


def test_configured_cost_threshold_and_unknown_retry_reserve(tmp_path):
    from agent_evolve.baseline import ProviderError

    budget = Budget.create(
        tmp_path / "budget.json", limit=5000, cost_limit_rmb=50, phase_limits={"baseline": 5000}
    )
    state = budget.read()
    state.update(cost_rmb=31, predecessor={"snapshot": "fixture"})
    budget.save(state)
    event = budget.begin("baseline", "agent", "fixture")
    budget.finish(event, response={"usage": {"prompt_tokens": 1, "completion_tokens": 1}})
    assert budget.read()["stopped"] is None
    event = budget.begin("baseline", "agent", "fixture")
    budget.finish(event, error="Synthetic503", status_code=503, retryable=True)
    assert budget.read()["unknown_usage_requests"] == 1
    assert budget.read()["cost_rmb"] > 35.8 and budget.read()["stopped"] is None
    event = budget.begin("baseline", "agent", "last attempt")
    with pytest.raises(ProviderError):
        budget.finish(event, error="Synthetic503", status_code=503)
    assert budget.read()["requests"] == 3 and budget.read()["stopped"]


def test_buffered_request_reserve_does_not_rewrite_prior_occupancy(tmp_path):
    budget = Budget.create(
        tmp_path / "budget.json", limit=5000, cost_limit_rmb=50, phase_limits={"baseline": 5000}
    )
    state = budget.read()
    state.update(
        cost_rmb=23.5,
        predecessor={"snapshot": "synthetic"},
        unknown_cost_reserve_rmb=19.4,
        unknown_usage_requests=4,
    )
    budget.save(state)
    event = budget.begin("baseline", "agent", "fixture")
    budget.finish(
        event, error="Synthetic500", status_code=500, retryable=True, input_estimate=20_000
    )
    assert budget.read()["cost_rmb"] == pytest.approx(23.5 + 0.145152)
    assert budget.read()["unknown_cost_reserve_rmb"] > 19.4
    event = budget.begin("baseline", "agent", "fixture")
    budget.finish(
        event, response={"usage": {"prompt_tokens": 11, "completion_tokens": 1}}, input_estimate=10
    )
    assert budget.read()["stopped"] == "input_estimate_insufficient"
