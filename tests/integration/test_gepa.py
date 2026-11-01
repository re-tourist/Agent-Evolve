"""Real pinned GEPA, fake reflection; τ subprocess tests are an additional explicit opt-in."""

import importlib.util
import json
import os
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from agent_evolve.baseline import TAU_SHA, Config, deny_network, digest, write_json
from agent_evolve.optimization import (
    OptimizationConfig,
    export_result,
    optimize,
    verify_gepa,
)

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_GEPA_TESTS") != "1", reason="Opt in in the pinned GEPA environment"
)


@pytest.fixture
def config(tmp_path):
    baseline = Config(
        mode="mock",
        backend="tau",
        task_ids=("0",),
        instruction="seed",
        output_dir=str(tmp_path),
        run_id="unused",
        tau_checkout=str(ROOT / ".cache/tau2-source"),
    )
    write_json(tmp_path / "baseline.json", asdict(baseline))
    write_json(
        tmp_path / "splits.json",
        {"train": ["0"], "validation": ["1"], "test": ["TEST_SECRET"], "tau_sha": TAU_SHA},
    )
    (tmp_path / "seed.txt").write_text("seed", encoding="utf-8")
    return OptimizationConfig(
        baseline_file=str(tmp_path / "baseline.json"),
        seed_prompt_file=str(tmp_path / "seed.txt"),
        splits_file=str(tmp_path / "splits.json"),
        gepa_checkout=str(ROOT / ".cache/gepa-source"),
        tau_python=str(ROOT / "environments/tau/.venv/Scripts/python.exe"),
        output_dir=str(tmp_path / "runs"),
        run_id="gepa-test",
        seed=17,
        max_evals=6,
    )


def synthetic_worker(config, directory, python, timeout):
    # Explicitly injected synthetic test score, never described as official benchmark evidence.
    assert config.seed == 17  # optimization seed must reach M2, not inherit baseline seed 42
    return (
        {
            "task_id": config.task_ids[0],
            "mode": "mock",
            "backend": "tau",
            "prompt_sha256": digest(config.instruction),
            "status": "task_success" if "revision" in config.instruction else "task_failure",
            "official_task_reward": float("revision" in config.instruction),
            "evaluation_details": {"reward": float("revision" in config.instruction)},
            "excluded_from_task_metrics": False,
            "reward_source": "official_evaluator_on_scripted_trace",
            "messages": [],
        },
        {
            "instruction_sha256": digest(config.instruction),
            "policy_sha256": "fixed-synthetic-policy",
        },
        {"upstream_sha": TAU_SHA},
    )


@pytest.mark.parametrize("feedback_mode", ["basic", "structured"])
def test_real_api_loop_candidate_lineage_and_split_secrecy(config, feedback_mode):
    config = replace(config, feedback_mode=feedback_mode)
    with deny_network():
        verify_gepa(config.gepa_checkout)
        assert importlib.util.find_spec("litellm") is None  # GEPA core only, no provider SDK
        directory = optimize(config, worker=synthetic_worker)
        from gepa.core.result import GEPAResult

        result = GEPAResult.from_dict(json.loads((directory / "gepa_result.json").read_text()))
    summary = json.loads((directory / "summary.json").read_text())
    assert result.best_score == 1.0 and "revision" in result.best_candidate
    assert len(result.candidates) == 2 and result.parents[1] == [0]
    assert summary["evaluations"] == summary["gepa_total_evals"] == 4
    assert summary["reflection_calls"] == 1 and summary["test_evaluated"] is False
    reflection = json.loads((directory / "reflection-0001.json").read_text())
    assert "TEST_SECRET" not in json.dumps(reflection)
    records = [
        json.loads(line) for line in (directory / "evaluations.jsonl").read_text().splitlines()
    ]
    assert {r["example"]["id"] for r in records} == {"0", "1"}
    assert all(r["transport"] == "injected_test_worker" for r in records)
    assert all(
        ("structured_feedback" in r["feedback"]) == (feedback_mode == "structured") for r in records
    )
    assert (directory / "gepa_eval_log.json").exists() and (
        directory / "gepa_metadata.json"
    ).exists()
    with pytest.raises(FileExistsError):
        optimize(config, worker=synthetic_worker)


@pytest.mark.parametrize("limit", [1, 2])
def test_real_gepa_budget_exhaustion_never_overshoots(config, limit):
    directory = optimize(replace(config, max_evals=limit), worker=synthetic_worker)
    summary = json.loads((directory / "summary.json").read_text())
    assert summary["evaluations"] == limit
    assert summary["budget"]["exhausted"] is True
    assert summary["stop_reason"] == "eval_budget_exhausted"


def test_real_engine_failure_aborts_no_zero_candidate(config):
    def failed(*args):
        raise ConnectionError("private-provider-detail")

    with pytest.raises(ConnectionError):
        optimize(config, worker=failed)
    directory = Path(config.output_dir) / config.run_id
    summary = json.loads((directory / "summary.json").read_text())
    assert summary["score"] is None and summary["status"] == "error"
    assert not (directory / "best_candidate.json").exists()
    assert "private-provider-detail" not in (directory / "summary.json").read_text()


def test_public_api_keyword_contract_and_result_roundtrip(tmp_path):
    with deny_network():
        from gepa.optimize_anything import OptimizeAnythingConfig, optimize_anything

        reflection = []

        def local_model(prompt):
            reflection.append(prompt)
            return "next instruction"

        result = optimize_anything(
            seed_candidate="seed",
            evaluator=lambda c, e: (0.0, {"kind": "fixture"}),
            dataset=[{"id": "train"}],
            valset=[{"id": "val"}],
            test_set=None,
            config=OptimizeAnythingConfig(
                max_evals=4,
                max_concurrency=1,
                output_dir=tmp_path / "oa",
                run_dir=str(tmp_path / "state"),
                engine_config={
                    "engine": {
                        "parallel": False,
                        "use_cloudpickle": False,
                        "max_candidate_proposals": 1,
                    },
                    "reflection": {"reflection_lm": local_model, "reflection_minibatch_size": 1},
                },
            ),
        )
        export_result(result, tmp_path)
    assert reflection
    assert result.best_candidate == "seed"  # no fabricated improvement for equal fixture scores
    assert result.total_evals == 3
    assert result.metadata["engine"] == "gepa"
    assert result.candidates and result.eval_log


@pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_WORKER_TESTS") != "1",
    reason="Requires the separately pinned M2 environment; no API",
)
def test_official_retail_worker_and_prompt_tools_history(config):
    # Actual worker used once; other offline engine tests use explicit synthetic fixtures.
    from agent_evolve.gepa_adapter import CandidateLedger, TaskSets, TauEvaluator

    ledger_dir = Path(config.output_dir)
    ledger_dir.mkdir()
    ledger = CandidateLedger(ledger_dir)
    evaluator = TauEvaluator(
        Config.load(Path(config.baseline_file)),
        TaskSets(("0",), ("1",), ("5",)),
        ledger,
        config.tau_python,
        max_evals=1,
    )
    score, feedback = evaluator("Candidate instruction", {"id": "0", "split": "train"})
    assert score == 0.0 and feedback["message_count"] >= 6
    assert feedback["tool_names"] == ["get_order_details"]
    assert feedback["score_source"] == "official_m2_subprocess"
    assert (ledger_dir / feedback["trace_path"] / "0.raw.json").exists()
