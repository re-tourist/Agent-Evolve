"""M3-A real GEPA engine with deterministic reflection and M2 scripted evaluation only."""

import argparse
import importlib.metadata
import json
import platform
import re
import subprocess
import time
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from agent_evolve.baseline import (
    Config,
    LiveNotApprovedError,
    ProviderError,
    deny_network,
    digest,
    git_info,
    write_json,
)
from agent_evolve.gepa_adapter import CandidateLedger, TaskSets, TauEvaluator, candidate_text

GEPA_SHA = "8c7b697a71977980afc7537dac0881e784eef99f"


@dataclass(frozen=True)
class OptimizationConfig:
    baseline_file: str
    seed_prompt_file: str
    splits_file: str
    gepa_checkout: str
    tau_python: str
    output_dir: str
    run_id: str
    mode: str = "offline"
    seed: int = 42
    max_evals: int = 4
    max_proposals: int = 1
    worker_timeout: int = 90
    acceptance_criterion: str = "strict_improvement"
    reflection_mode: str = "deterministic_fake"
    feedback_mode: str = "basic"

    def __post_init__(self):
        if self.feedback_mode not in {"basic", "structured"}:
            raise ValueError("feedback_mode must be basic or structured")
        if self.mode not in {"offline", "live"}:
            raise ValueError("Mode must be offline or live")
        if self.reflection_mode != "deterministic_fake":
            raise ValueError("M3-A permits only the local reflection fake")
        if self.acceptance_criterion not in {"strict_improvement", "improvement_or_equal"}:
            raise ValueError("Invalid GEPA acceptance criterion")
        if not isinstance(self.run_id, str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,80}", self.run_id
        ):
            raise ValueError("Invalid optimization run ID")
        for value, low, high in [
            (self.seed, 0, 2**32 - 1),
            (self.max_evals, 1, 20),
            (self.max_proposals, 1, 5),
            (self.worker_timeout, 1, 180),
        ]:
            if type(value) is not int or not low <= value <= high:
                raise ValueError("Invalid seed/evaluation/proposal/timeout limit")

    @classmethod
    def load(cls, filename):
        path = Path(filename)
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in (
            "baseline_file",
            "seed_prompt_file",
            "splits_file",
            "gepa_checkout",
            "tau_python",
            "output_dir",
        ):
            data[key] = str((path.parent / data[key]).resolve())
        return cls(**data)


def verify_gepa(checkout):
    checkout = Path(checkout).resolve()

    def git(*args):
        return subprocess.check_output(
            ["git", "-C", str(checkout), *args], text=True, timeout=5
        ).strip()

    if git("rev-parse", "HEAD") != GEPA_SHA or git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("GEPA source must match its pin and have no tracked modifications")
    import gepa

    if not Path(gepa.__file__).resolve().is_relative_to(checkout):
        raise ValueError("Installed GEPA must come from the audited editable checkout")
    if importlib.metadata.version("gepa") != "0.1.4":
        raise ValueError("Unexpected GEPA package version")


class OfflineReflection:
    """Official callable-LM seam; fixed proposals, not an LLM or feedback analysis."""

    total_cost = 0.0

    def __init__(self, directory, seed_text):
        self.directory, self.seed_text, self.calls = Path(directory), seed_text, 0

    def __call__(self, prompt):
        self.calls += 1
        proposal = (
            self.seed_text + f"\nOffline revision {self.calls}: inspect tool results carefully."
        )
        write_json(
            self.directory / f"reflection-{self.calls:04d}.json",
            {
                "kind": "deterministic_fake",
                "input": prompt,
                "output": proposal,
                "tokens": "unavailable; no tokenizer/model executed",
                "api_calls": 0,
            },
        )
        return proposal


def export_result(result, directory):
    # to_dict omits runtime metadata/eval_log, so persist those separately and without coercion.
    write_json(directory / "gepa_result.json", result.to_dict())
    write_json(directory / "gepa_metadata.json", result.metadata)
    write_json(directory / "gepa_eval_log.json", result.eval_log)
    pool = []
    for index, candidate in enumerate(result.candidates):
        pool.append(
            {
                "index": index,
                "candidate": candidate,
                "parents": result.parents[index],
                "validation_score": result.val_aggregate_scores[index],
            }
        )
    write_json(directory / "candidate_pool.json", pool)
    write_json(
        directory / "best_candidate.json",
        {
            "instruction": result.best_candidate,
            "sha256": digest(candidate_text(result.best_candidate)),
            "best_index": result.best_idx,
            "validation_score": result.best_score,
            "basis": "official GEPA validation selection",
        },
    )


def optimize(config, *, worker=None):
    if config.mode == "live":
        raise LiveNotApprovedError("M3-A: live disabled; separate staged M3-B approval required")
    with deny_network():
        verify_gepa(config.gepa_checkout)
        from gepa.optimize_anything import OptimizeAnythingConfig, optimize_anything

        splits = TaskSets.load(config.splits_file)
        baseline = replace(Config.load(Path(config.baseline_file)), seed=config.seed)
        seed = candidate_text(Path(config.seed_prompt_file).read_text(encoding="utf-8"))
        # Validate role and paths before reserving run artifacts; Config remains M2's validator.
        if baseline.mode != "mock" or baseline.backend != "tau":
            raise ValueError("M3-A baseline must be scripted official tau")
        if not worker and not Path(config.tau_python).is_file():
            raise ValueError("Pinned tau environment Python not found")
        directory = Path(config.output_dir) / config.run_id
        directory.mkdir(parents=True, exist_ok=False)
        ledger = CandidateLedger(directory)
        ledger.candidate(seed)
        write_json(directory / "config.json", asdict(config))
        write_json(directory / "baseline_config.json", asdict(baseline))
        write_json(directory / "splits.json", asdict(splits))
        write_json(directory / "seed_prompt.json", {"instruction": seed, "sha256": digest(seed)})
        write_json(
            directory / "metadata.json",
            {
                "run_id": config.run_id,
                "created_utc": datetime.now(UTC).isoformat(),
                "git": git_info(),
                "gepa_version": importlib.metadata.version("gepa"),
                "tau_version": "2.0.0; worker metadata verifies actual source",
                "gepa_sha": GEPA_SHA,
                "tau_sha": splits.tau_sha,
                "python": platform.python_version(),
                "mode": "offline",
                "reflection": "deterministic_fake",
                "agent": baseline.agent_model,
                "simulator": baseline.user_model,
                "judge": "none; judge tasks refused by M2",
                "transport": "injected_test_worker" if worker else "official_m2_subprocess",
                "test_evaluated": False,
                "real_model_calls": 0,
                "token_usage": "unavailable",
                "source_of_score": "mock_test_injection"
                if worker
                else "official_reward_scripted_trace",
            },
        )
        evaluator = TauEvaluator(
            baseline,
            splits,
            ledger,
            config.tau_python,
            max_evals=config.max_evals,
            timeout=config.worker_timeout,
            worker=worker,
            feedback_mode=config.feedback_mode,
        )
        reflection = OfflineReflection(directory, seed)
        start = time.monotonic()
        try:
            result = optimize_anything(
                seed_candidate=seed,
                evaluator=evaluator,
                dataset=splits.examples("train"),
                valset=splits.examples("validation"),
                test_set=None,
                objective="Optimize Instructions only; Policy/tools/tasks/reward stay fixed.",
                config=OptimizeAnythingConfig(
                    engine="gepa",
                    name=config.run_id,
                    max_evals=config.max_evals,
                    max_concurrency=1,
                    output_dir=directory / "gepa",
                    run_dir=str(directory / "gepa_state"),
                    engine_config={
                        "engine": {
                            "seed": config.seed,
                            "parallel": False,
                            "use_cloudpickle": False,
                            "raise_on_exception": True,
                            "cache_evaluation": False,
                            "max_candidate_proposals": config.max_proposals,
                            "acceptance_criterion": config.acceptance_criterion,
                        },
                        "reflection": {"reflection_lm": reflection, "reflection_minibatch_size": 1},
                    },
                ),
            )
            export_result(result, directory)
            summary = {
                "status": "complete",
                "engine": "real_gepa_offline",
                "best_candidate_sha256": digest(result.best_candidate),
                "best_score": result.best_score,
                "evaluations": ledger.attempts,
                "gepa_total_evals": result.total_evals,
                "budget": result.metadata.get("budget", "unavailable"),
                "stop_reason": "eval_budget_exhausted"
                if result.metadata.get("budget", {}).get("exhausted")
                else "proposal_limit_or_engine_stop; see GEPA state",
                "reflection_calls": reflection.calls,
                "test_evaluated": False,
                "real_model_calls": 0,
                "token_usage": "unavailable",
                "benchmark_claim": False,
                "seconds": time.monotonic() - start,
            }
        except Exception as exc:
            write_json(
                directory / "summary.json",
                {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "score": None,
                    "best_candidate": "unavailable; run aborted",
                    "evaluations": ledger.attempts,
                    "reflection_calls": reflection.calls,
                    "seconds": time.monotonic() - start,
                    "real_model_calls": 0,
                },
            )
            raise
        write_json(directory / "summary.json", summary)
        return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        directory = optimize(OptimizationConfig.load(args.config))
    except Exception as exc:
        # No raw provider exception text or credential-bearing config values to stdout.
        parser.exit(
            2, f"{type(exc).__name__}: optimization refused/aborted; inspect saved evidence\n"
        )
    print(f"Artifacts: {directory}")
    return 0


def optimize_live(client, phase, seed, splits):
    """Authorized sprint-only entry; legacy standalone Live gate remains closed."""
    from gepa.optimize_anything import OptimizeAnythingConfig, optimize_anything

    from agent_evolve.experiment import LiveEvaluator, QwenReflection
    from agent_evolve.live_runtime import PHASE_LIMITS, StageBudget

    settings = getattr(client, "config", {}).get("search", {})
    max_evals = settings.get("max_evals", 8)
    batch_size = settings.get("minibatch", 1)
    proposals = settings.get("max_proposals", 2)
    reflection_options = {
        "reflection_lm": None,
        "reflection_minibatch_size": batch_size,
        "skip_perfect_score": False,
    }
    if getattr(client, "config", {}).get("tau_protocol") == "reviewed-en-text":
        reflection_options["skip_perfect_score"] = True
        reflection_options["perfect_score"] = 1.0
    if hasattr(client, "sampler"):
        reflection_options["batch_sampler"] = client.sampler(phase)

    if phase not in {"basic", "structured"}:
        raise ValueError("Invalid search phase")
    directory = client.directory / phase
    directory.mkdir(exist_ok=False)
    ledger = CandidateLedger(directory)
    ledger.candidate(seed)
    evaluator = LiveEvaluator(client, phase, ledger, splits)
    reflection = QwenReflection(client, phase, directory)
    reflection_options["reflection_lm"] = reflection

    def stop(state):
        budget = client.budget.read()
        return (
            max_evals - ledger.attempts < 2 * batch_size + len(splits.validation)
            or budget["stopped"] is not None
            or min(
                budget["limit"] - budget["requests"],
                budget.get("phase_limits", PHASE_LIMITS)[phase] - budget["phases"][phase],
            )
            < budget.get("task_calls", 24)
            * (2 * batch_size + len(splits.validation) if settings else 1)
        )

    try:
        result = optimize_anything(
            seed_candidate=seed,
            evaluator=evaluator,
            dataset=splits.examples("train"),
            valset=splits.examples("validation"),
            test_set=None,
            objective="Optimize Agent Instructions; respect fixed Policy, tools and scoring.",
            config=OptimizeAnythingConfig(
                engine="gepa",
                max_evals=max_evals,
                max_concurrency=1,
                name=phase,
                output_dir=directory / "gepa",
                run_dir=str(directory / "gepa_state"),
                engine_config={
                    "engine": {
                        "seed": 42,
                        "parallel": False,
                        "use_cloudpickle": False,
                        "raise_on_exception": True,
                        "cache_evaluation": False,
                        "max_candidate_proposals": proposals,
                        "acceptance_criterion": "strict_improvement",
                    },
                    "reflection": reflection_options,
                    "stop_callbacks": [stop],
                },
            ),
        )
    except StageBudget:
        from gepa.core.result import GEPAResult
        from gepa.core.state import GEPAState

        state = GEPAState.load(str(directory / "gepa_state"))
        result = GEPAResult.from_state(
            state,
            run_dir=str(directory / "gepa_state"),
            seed=42,
            str_candidate_key="current_candidate",
        )
    if client.budget.read()["stopped"]:
        raise ProviderError("Shared budget stopped")
    if len(result.val_subscores[result.best_idx]) != len(splits.validation):
        raise ValueError("Best candidate does not have complete validation")
    export_result(result, directory)
    events = [
        json.loads(line) for line in (directory / "evaluations.jsonl").read_text().splitlines()
    ]
    scored = [event for event in events if event["status"] == "scored"]
    new_hashes = {event["candidate_sha256"] for event in scored} - {digest(seed)}
    summary = {
        "phase": phase,
        "evaluations": len(events),
        "scored": len(scored),
        "new_candidates_evaluated": len(new_hashes),
        "unique_candidates_evaluated": len({event["candidate_sha256"] for event in scored}),
        "accepted_candidates_including_seed": len(result.candidates),
        "reflection_requests": reflection.calls,
        "train_tasks_observed": sorted(
            {event["example"]["id"] for event in scored if event["example"]["split"] == "train"}
        ),
        "best_sha256": digest(result.best_candidate),
        "best_validation_score": result.best_score,
        "best_complete_validation": True,
    }
    write_json(directory / "summary.json", summary)
    return {"best": result.best_candidate, "summary": summary}


if __name__ == "__main__":
    raise SystemExit(main())
