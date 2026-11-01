import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from agent_evolve.baseline import TAU_SHA, Config, LiveNotApprovedError, digest
from agent_evolve.gepa_adapter import (
    CandidateLedger,
    EvaluationLimit,
    EvaluationUnavailable,
    TaskSets,
    TauEvaluator,
    candidate_text,
    run_m2_worker,
)
from agent_evolve.optimization import OfflineReflection, OptimizationConfig, optimize


@pytest.fixture
def splits():
    return TaskSets(("0",), ("1",), ("5",))


@pytest.fixture
def evaluator(tmp_path, splits):
    baseline = Config(
        mode="mock",
        backend="tau",
        task_ids=("0",),
        instruction="seed",
        output_dir=str(tmp_path),
        run_id="unused",
    )
    ledger = CandidateLedger(tmp_path)
    return TauEvaluator(baseline, splits, ledger, "unused-python", max_evals=4, worker=fake_worker)


def fake_worker(config, directory, python, timeout):
    """Unit fixture, not actual official scoring; transport is tagged test injection."""
    return (
        {
            "task_id": config.task_ids[0],
            "mode": "mock",
            "backend": "tau",
            "prompt_sha256": digest(config.instruction),
            "official_task_reward": 0.0,
            "evaluation_details": {"reward": 0.0},
            "status": "task_failure",
            "excluded_from_task_metrics": False,
            "reward_source": "official_evaluator_on_scripted_trace",
            "messages": [],
        },
        {"instruction_sha256": digest(config.instruction), "policy_sha256": "fixed-test-policy"},
        {"upstream_sha": TAU_SHA},
    )


@pytest.mark.parametrize("candidate", [None, "", " ", 0, {}, {"policy": "rewrite"}, "a" * 8193])
def test_invalid_candidate(candidate):
    with pytest.raises(ValueError):
        candidate_text(candidate)


def test_splits_are_disjoint_and_test_never_admitted(splits, evaluator):
    with pytest.raises(ValueError):
        TaskSets(("0",), ("0",), ("5",))
    with pytest.raises(ValueError):
        splits.examples("test")
    with pytest.raises(ValueError):
        evaluator("candidate", {"id": "5", "split": "test"})
    with pytest.raises(ValueError):
        evaluator("candidate", {"id": "5", "split": "train"})
    assert evaluator.ledger.attempts == 0


def test_official_score_contract_and_candidate_history(evaluator):
    a, feedback = evaluator("first", {"id": "0", "split": "train"})
    b, _ = evaluator("second", {"id": "1", "split": "validation"})
    assert a == b == 0.0
    assert feedback["score_source"] == "injected_test_worker"
    assert "evaluation_details" not in feedback  # no gold DB/evaluator internals to reflection
    records = [
        json.loads(s)
        for s in (evaluator.ledger.directory / "evaluations.jsonl").read_text().splitlines()
    ]
    assert len(records) == 2
    assert records[0]["candidate_sha256"] != records[1]["candidate_sha256"]
    assert len(list((evaluator.ledger.directory / "candidates").glob("*.json"))) == 2


@pytest.mark.parametrize(
    "override",
    [
        {"official_task_reward": None},
        {"official_task_reward": float("nan")},
        {"official_task_reward": True},
        {"official_task_reward": 2.0},
        {"excluded_from_task_metrics": True},
        {"status": "infrastructure_error"},
        {"task_id": "different"},
        {"reward_source": "made_up_weighted_score"},
        {"evaluation_details": None},
        {"evaluation_details": {"reward": 0.5}},
    ],
)
def test_invalid_or_missing_scores_do_not_become_zero(evaluator, override):
    def worker(*args):
        result, prompt, metadata = fake_worker(*args)
        result.update(override)
        return result, prompt, metadata

    evaluator.worker = worker
    with pytest.raises(EvaluationUnavailable):
        evaluator("candidate", {"id": "0", "split": "train"})
    event = json.loads(
        (evaluator.ledger.directory / "evaluations/000001/evaluation.json").read_text()
    )
    assert event["score"] is None and event["status"] == "error"


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError, RuntimeError])
def test_worker_errors_abort_without_score(evaluator, error):
    def worker(*args):
        raise error("sentinel-private-detail")

    evaluator.worker = worker
    with pytest.raises(error):
        evaluator("candidate", {"id": "0", "split": "train"})
    event = json.loads(
        (evaluator.ledger.directory / "evaluations/000001/evaluation.json").read_text()
    )
    assert event["score"] is None
    assert "sentinel-private-detail" not in json.dumps(event)


def test_policy_contamination_aborts_and_budget_is_admission_limit(evaluator):
    evaluator("first", {"id": "0", "split": "train"})

    def changed(*args):
        result, prompt, metadata = fake_worker(*args)
        prompt["policy_sha256"] = "contaminated"
        return result, prompt, metadata

    evaluator.worker = changed
    with pytest.raises(EvaluationUnavailable, match="Policy"):
        evaluator("second", {"id": "0", "split": "train"})
    evaluator.max_evals = 2
    with pytest.raises(EvaluationLimit):
        evaluator("third", {"id": "0", "split": "train"})
    assert evaluator.ledger.attempts == 2


def test_fake_reflection_preserves_actual_prompt_and_proposal(tmp_path):
    fake = OfflineReflection(tmp_path, "seed")
    value = fake([{"role": "user", "content": "train feedback"}])
    assert "Offline revision 1" in value
    record = json.loads((tmp_path / "reflection-0001.json").read_text())
    assert record["input"][0]["content"] == "train feedback"
    assert record["output"] == value and record["api_calls"] == 0


@pytest.fixture
def optimization_config(tmp_path):
    return OptimizationConfig(
        **{
            key: str(tmp_path / key)
            for key in [
                "baseline_file",
                "seed_prompt_file",
                "splits_file",
                "gepa_checkout",
                "tau_python",
                "output_dir",
            ]
        },
        run_id="run",
    )


def test_live_denial_precedes_source_import_and_file_reads(optimization_config, monkeypatch):
    monkeypatch.setenv("AGENT_EVOLVE_LIVE_APPROVED", "true")
    with pytest.raises(LiveNotApprovedError):
        optimize(replace(optimization_config, mode="live"))
    assert not (Path(optimization_config.output_dir) / "run").exists()


@pytest.mark.parametrize(
    "override",
    [
        {"max_evals": 0},
        {"max_evals": True},
        {"seed": -1},
        {"max_proposals": 999},
        {"reflection_mode": "paid/model"},
        {"run_id": "../x"},
        {"acceptance_criterion": "ignore_policy"},
    ],
)
def test_optimization_config_rejects_unsafe_options(optimization_config, override):
    with pytest.raises(ValueError):
        replace(optimization_config, **override)


def test_config_load_defaults_offline_and_rejects_extra_keys(optimization_config, tmp_path):
    data = asdict(optimization_config)
    data.pop("mode")
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    assert OptimizationConfig.load(path).mode == "offline"
    data["api_key"] = "private"
    path.write_text(json.dumps(data))
    with pytest.raises(TypeError):
        OptimizationConfig.load(path)


def test_worker_timeout_is_retained_without_zero_score(evaluator, tmp_path, monkeypatch):
    import subprocess

    def expired(*args, **kwargs):
        raise subprocess.TimeoutExpired("synthetic worker", 1)

    monkeypatch.setattr("agent_evolve.gepa_adapter.subprocess.run", expired)
    with pytest.raises(EvaluationUnavailable, match="timeout"):
        run_m2_worker(evaluator.baseline, tmp_path, Path("unused"), 1)
    assert json.loads((tmp_path / "worker.json").read_text())["score"] is None


def test_optimization_cli_live_refusal(optimization_config, tmp_path):
    import subprocess
    import sys

    path = tmp_path / "live.json"
    path.write_text(json.dumps(asdict(replace(optimization_config, mode="live"))))
    result = subprocess.run(
        [sys.executable, "-m", "agent_evolve.optimization", "--config", str(path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "LiveNotApprovedError" in result.stderr
    assert not Path(optimization_config.output_dir).exists()


def test_optional_structured_feedback_preserves_score_and_refuses_test(evaluator):
    from agent_evolve.feedback import diagnose

    basic_score, basic = evaluator("candidate", {"id": "0", "split": "train"})
    assert "structured_feedback" not in basic
    evaluator.feedback_mode = "structured"
    score, structured = evaluator("candidate", {"id": "0", "split": "train"})
    expected = diagnose(fake_worker(evaluator.baseline, None, None, None)[0])
    assert score == basic_score == 0.0
    assert structured.pop("structured_feedback") == expected
    # Other fields are unchanged except the per-evaluation trace locator.
    structured.pop("trace_path")
    basic.pop("trace_path")
    assert structured == basic
    with pytest.raises(ValueError):
        evaluator("candidate", {"id": "5", "split": "test"})


def test_invalid_feedback_mode(optimization_config):
    with pytest.raises(ValueError):
        replace(optimization_config, feedback_mode="judge")
