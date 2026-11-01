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
