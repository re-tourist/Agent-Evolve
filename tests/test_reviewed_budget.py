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


def test_reschedule_reuses_completed_episode_without_task_or_counter_reset(tmp_path, monkeypatch):
    from agent_evolve import optimization, study
    from agent_evolve.baseline import digest, write_json

    source = tmp_path / "old"
    source.mkdir()
    seed = tmp_path / "seed.txt"
    seed.write_text("seed", encoding="utf-8")
    config = {
        "gepa_checkout": "unused",
        "credentials_dir": "unused",
        "output_dir": str(tmp_path),
        "run_id": "old",
        "tau_protocol": "reviewed-en-text",
        "budget_predecessor": str(tmp_path / "prior.json"),
        "request_limit": 5000,
        "cost_limit_rmb": 50,
        "task_limits": {"calls": 48},
        "seed_file": str(seed),
        "seed": 42,
        "train": ["1"],
        "validation": ["2"],
        "test": ["3"],
    }
    write_json(source / "config.json", config)
    write_json(source / "summary.json", {"search": {}, "test": []})
    old = Budget.create(
        source / "budget.json", limit=5000, cost_limit_rmb=50, phase_limits={"baseline": 5000}
    )
    state = old.read()
    state.update(requests=998, cost_rmb=24.33, stopped="InternalServerError")
    old.save(state)
    prior = old.path.read_bytes()
    task = source / "baseline/1/task"
    task.mkdir(parents=True)
    write_json(task / "1.raw.json", {"reward_info": {"reward": 0}})
    calls = []

    class Client(study.StudyClient):
        def task(self, *args):
            pytest.fail("Completed task must not be executed again")

        def read_task(self, *args):
            calls.append("read")
            return 0, {"termination_reason": "user_stop"}, {"prompt_sha256": digest("seed")}, {}, {}

        def semantic_feedback(self, result, prompt, directory, example):
            calls.append("diagnostic")
            return {
                "diagnostics": [],
                "candidate_sha256": digest("seed"),
                "evidence_source": "baseline/1/semantic-recovery/observable.json",
            }

    monkeypatch.setattr(optimization, "verify_gepa", lambda _: None)
    monkeypatch.setattr(study, "credentials", lambda _: ("fixture", "https://offline.invalid"))
    monkeypatch.setattr(study, "StudyClient", Client)

    def stop_before_search(*args):
        raise ValueError("Synthetic stop before any search")

    monkeypatch.setattr(study, "run_search", stop_before_search)
    config.update(run_id="new", budget_predecessor=str(old.path), baseline_source_run=str(source))
    result = study.run(config, live=True)
    assert result["status"] == "stopped" and calls == ["read", "diagnostic"]
    assert Budget(tmp_path / "new/budget.json").read()["requests"] == 998
    assert old.path.read_bytes() == prior
    assert (tmp_path / "new/baseline/1/reused_episode.json").exists()
    config["seed"] = 43
    with pytest.raises(ValueError, match="same-config"):
        study.run(config, live=True)
