"""Failure-driven semantic feedback study, reusing the pinned official task/search path."""

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path

from agent_evolve.baseline import TAU_SHA, digest, git_info, write_json
from agent_evolve.experiment import WorkerClient, run_search
from agent_evolve.gepa_adapter import TaskSets, candidate_text
from agent_evolve.live_runtime import Budget, credentials
from agent_evolve.qwen_smoke import MODEL, ROOT
from agent_evolve.semantic import (
    SYSTEM,
    deterministic_observations,
    observable_view,
    validate_analysis,
)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def algorithm_evidence(directory):
    """A/B/C evidence from actual artifacts; a boolean summary alone is insufficient."""
    directory = Path(directory)
    review_file = directory / "analysis/semantic_acceptance.json"
    if not review_file.exists():
        raise ValueError("GateA: a supported semantic case needs an explicit trace/Policy review")
    review = read(review_file)
    if review.get("status") != "supported" or not review.get("notes"):
        raise ValueError("GateA: semantic acceptance is unproven")
    for phase in ("basic", "structured"):
        s = read(directory / phase / "summary.json")
        if (
            s["new_candidates_evaluated"] < 2
            or len(s["train_tasks_observed"]) < 3
            or not s["best_complete_validation"]
        ):
            raise ValueError("GateC: insufficient real exploration/validation")
    events = [
        (p, read(p))
        for p in sorted((directory / "structured/evaluations").glob("*/evaluation.json"))
    ]
    seed_sha = read(directory / "seed_prompt.json")["sha256"]
    for source_path, event in events:
        if event.get("score") != 0 or event["example"]["split"] != "train":
            continue
        semantic = event.get("feedback", {}).get("structured_feedback", {})
        for d in semantic.get("diagnostics", []):
            if d.get("semantic_review") != "independent_second_pass" or d["category"] == "unknown":
                continue
            if review.get("source_evaluation") != str(
                source_path.relative_to(directory)
            ) or review.get("observation_sha256") != digest(d["observation"]):
                continue
            for effective in sorted(
                (directory / "structured").glob("reflection-*/effective_input.json")
            ):
                messages = read(effective)
                actual = (
                    messages
                    if isinstance(messages, str)
                    else "\n".join(m.get("content", "") for m in messages)
                )
                if d["observation"] not in actual or event["candidate_sha256"] not in actual:
                    continue
                output = effective.parent / "output.json"
                generated = read(output)["text"]
                subsequent = [
                    e
                    for p, e in events
                    if e.get("status") == "scored"
                    and e["candidate_sha256"] != seed_sha
                    and e["candidate_sha256"] != event["candidate_sha256"]
                    and p.stat().st_mtime > output.stat().st_mtime
                    and read(
                        directory / "structured/candidates" / (e["candidate_sha256"] + ".json")
                    )["instruction"].strip()
                    in generated
                ]
                if not subsequent:
                    continue
                return {
                    "A": {
                        "failed_evaluation": str(source_path.relative_to(directory)),
                        "category": d["category"],
                        "responsibility": d["responsibility"],
                        "evidence_source": semantic["evidence_source"],
                    },
                    "B": {
                        "actual_reflection_input": str(effective.relative_to(directory)),
                        "candidate_evaluations": [
                            {
                                "candidate_sha256": e["candidate_sha256"],
                                "task_id": e["example"]["id"],
                                "official_reward": e["score"],
                            }
                            for e in subsequent
                        ],
                    },
                    "C": {p: read(directory / p / "summary.json") for p in ("basic", "structured")},
                    "limitation": "Evidence flow and citations verified; semantic correctness "
                    "still needs human review.",
                }
    raise ValueError(
        "GatesA/B: no reviewed real failure linked to actual Reflection and candidate evaluation"
    )


def load(filename):
    filename = Path(filename).resolve()
    config = read(filename)
    for k in ("output_dir", "credentials_dir", "gepa_checkout", "tau_python", "seed_file"):
        config[k] = str((filename.parent / config[k]).resolve())
    TaskSets(*(tuple(config[k]) for k in ("train", "validation", "test")))
    if (
        config.get("study") != "semantic-v1"
        or not config["run_id"].replace("-", "").isalnum()
        or not 1 <= config["request_limit"] <= 5000
        or not 0 < config["cost_limit_rmb"] <= 50
        or not 1 <= config["task_limits"]["steps"] <= 64
        or not 1 <= config["task_limits"]["calls"] <= 64
        or not 30 <= config["task_limits"]["seconds"] <= 1200
        or not 2 <= config["search"]["minibatch"] <= 3
        or not 25 <= config["search"]["max_evals"] <= 40
        or not 2 <= config["search"]["max_proposals"] <= 8
        or not 1 <= config["trials"] <= 2
    ):
        raise ValueError("Study configuration exceeds approved scope")
    if set(config["test"]) & {"0", "5", "8", "9", "10", "12"}:
        raise ValueError("Previously inspected tasks cannot be new Test")
    if not 30 <= config.get("analysis_request_seconds", 30) <= 90:
        raise ValueError("Analysis request timeout exceeds approved bounded recovery")
    for k in ("diagnostic_tokens", "reflection_tokens"):
        if not 256 <= config[k] <= 4096:
            raise ValueError("Invalid output limit")
    # Judge eligibility and official split only: never inspect Test goals/answers.
    data = ROOT / ".cache/tau2-source/data/tau2/domains/retail"
    splits = read(data / "split_tasks.json")
    tasks = {str(t["id"]): t for t in read(data / "tasks.json")}
    for group in ("train", "validation", "test"):
        official = "test" if group == "test" else "train"
        for task_id in config[group]:
            if task_id not in splits[official]:
                raise ValueError("Unofficial split")
            criteria = tasks[task_id].get("evaluation_criteria") or {}
            if criteria.get("nl_assertions") or "COMMUNICATE" in criteria.get("reward_basis", []):
                raise ValueError("Judge task outside approved study")
    return config


class FailureSampler:
    """Public GEPA BatchSampler seam: rotate failed + successful cases identically in arms."""

    def __init__(self, pool, size, path):
        self.pool, self.size, self.path = pool, size, Path(path)
        self.counts = Counter()
        self.round = 0

    def next_minibatch_ids(self, loader, state):
        ids = list(loader.all_ids())
        mapping = {i: loader.fetch([i])[0]["id"] for i in ids}
        ordered = sorted(ids, key=lambda i: (self.counts[i], ids.index(i)))
        failed = [i for i in ordered if self.pool[mapping[i]]["reward"] < 1]
        passed = [i for i in ordered if self.pool[mapping[i]]["reward"] == 1]
        selected = []
        for group in (failed, passed, ordered):
            available = [i for i in group if i not in selected]
            if available and len(selected) < self.size:
                selected.append(available[0])
        for i in ordered:
            if len(selected) >= self.size:
                break
            if i not in selected:
                selected.append(i)
        self.counts.update(selected)
        self.round += 1
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "round": self.round,
                        "tasks": [mapping[i] for i in selected],
                        "baseline_rewards": [self.pool[mapping[i]]["reward"] for i in selected],
                    }
                )
                + "\n"
            )
        return selected


class StudyClient(WorkerClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = {}

    def sampler(self, phase):
        return FailureSampler(
            self.pool, self.config["search"]["minibatch"], self.directory / phase / "sampled.jsonl"
        )

    def semantic_feedback(self, result, prompt, directory, example):
        if example["split"] == "test":
            raise ValueError("Test must not enter optimization diagnosis")
        directory = Path(directory)
        tools = read(directory / "task/tools.json")
        view = observable_view(result, prompt["policy"], tools)
        target = directory / "semantic"
        if target.exists():
            target = directory / "semantic-recovery"
        # Only observable content enters hosted diagnosis. Raw output remains private.
        phase = (
            "baseline" if directory.is_relative_to(self.directory / "baseline") else "structured"
        )
        self.execute(
            {
                "kind": "diagnostic",
                "directory": str(target),
                "phase": phase,
                "association": {
                    "candidate": result["prompt_sha256"],
                    "task": example["id"],
                    "source": str(directory.relative_to(self.directory)),
                },
                "max_tokens": self.config["diagnostic_tokens"],
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": json.dumps(view, ensure_ascii=False)},
                ],
            }
        )
        write_json(target / "observable.json", view)
        text = read(target / "output.json")["text"]
        try:
            analysis = validate_analysis(text, view)
        except (ValueError, TypeError, KeyError):
            analysis = {
                "diagnostics": [],
                "rejected": [{"reason": "invalid_model_json"}],
                "success_principles": [],
            }
        analysis.update(
            schema_version=2,
            deterministic=deterministic_observations(result),
            task_id=example["id"],
            candidate_sha256=result["prompt_sha256"],
            observable_sha256=digest(json.dumps(view, ensure_ascii=False)),
            evidence_source=str((target / "observable.json").relative_to(self.directory)),
        )
        prior = self.pool.get(example["id"])
        if prior and prior["reward"] < 1:
            # The real baseline failure remains informative even if a stochastic rerun passes.
            # It is labelled historical and cannot replace this execution's official scalar.
            analysis["historical_training_failure"] = {
                "official_reward": prior["reward"],
                "candidate_sha256": prior["diagnostic"]["candidate_sha256"],
                "current_candidate_same_as_failure": prior["diagnostic"]["candidate_sha256"]
                == result["prompt_sha256"],
                "diagnostics": prior["diagnostic"]["diagnostics"],
                "evidence_source": prior["diagnostic"]["evidence_source"],
                "note": "Earlier training observation, not this run's Reward or a gold answer.",
            }
        write_json(target / "analysis.json", analysis)
        return analysis


def run(config, *, live=False, resume=False):
    if not live:
        return {"status": "offline_config_only", "real_calls": 0}
    from agent_evolve.optimization import verify_gepa

    verify_gepa(config["gepa_checkout"])
    key, endpoint = credentials(config["credentials_dir"])
    directory = Path(config["output_dir"]) / config["run_id"]
    if resume:
        previous = read(directory / "summary.json")
        old_config = read(directory / "config.json")
        if {k: v for k, v in config.items() if k != "analysis_request_seconds"} != old_config:
            raise ValueError("Recovery may only extend the analysis request timeout")
        budget = Budget(directory / "budget.json")
        state = budget.read()
        events = [
            json.loads(line)
            for line in budget.path.with_suffix(".jsonl").read_text(encoding="utf-8").splitlines()
        ]
        failures = [e for e in events if e["status"] == "error"]
        if (
            state["stopped"] != "Timeout"
            or state["pending"] is not None
            or len(failures) != 1
            or failures[0]["role"] != "diagnostic"
            or failures[0]["phase"] != "baseline"
            or previous["search"]
            or previous["test"]
        ):
            raise ValueError("Recovery is restricted to one baseline diagnostic timeout")
        # Unknown Usage is NOT invented or erased. Reserve maximum context+output cost
        # at the highest Beijing tier, rather than silently undercounting the bill.
        reserve = 1_000_000 * 4.8 / 1_000_000 + old_config["diagnostic_tokens"] * 48 / 1_000_000
        write_json(
            directory / "recovery.json",
            {
                "kind": "one_bounded_diagnostic_recovery",
                "source_git": git_info(),
                "failed_request": failures[0]["request"],
                "prior_requests": state["requests"],
                "usage": "unavailable",
                "unknown_cost_upper_bound_rmb": reserve,
                "task_reexecuted": False,
                "reason": "30s local analysis deadline inadequate; allow one attempt at90s",
            },
        )
        write_json(directory / "config_revision_2.json", config)
        state.update(
            stopped=None,
            cost_rmb=state["cost_rmb"] + reserve,
            unknown_usage_requests=1,
            unknown_cost_reserve_rmb=reserve,
        )
        budget.save(state)
        budget.log(
            {
                "status": "recovery_reserve",
                "request": failures[0]["request"],
                "estimated_rmb": reserve,
                "usage": "unavailable",
            }
        )
    else:
        directory.mkdir(parents=True, exist_ok=False)
    phases = {p: config["request_limit"] for p in ("baseline", "basic", "structured", "test")}
    if not resume:
        Budget.create(
            directory / "budget.json",
            limit=config["request_limit"],
            cost_limit_rmb=config["cost_limit_rmb"],
            phase_limits=phases,
            task_calls=config["task_limits"]["calls"],
        )
        write_json(directory / "config.json", config)
        write_json(
            directory / "metadata.json",
            {
                "git": git_info(),
                "tau_sha": TAU_SHA,
                "model": MODEL,
                "test_sent_to_gepa": False,
                "judge": "none",
            },
        )
    seed = candidate_text(Path(config["seed_file"]).read_text(encoding="utf-8"))
    if not resume:
        write_json(directory / "seed_prompt.json", {"instruction": seed, "sha256": digest(seed)})
    env = dict(
        os.environ,
        DASHSCOPE_API_KEY=key,
        DASHSCOPE_BASE_URL=endpoint,
        PYTHONIOENCODING="utf-8",
        PYTHON_DOTENV_DISABLED="1",
        LITELLM_LOCAL_MODEL_COST_MAP="True",
    )
    client = StudyClient(config, directory, environment=env)
    splits = TaskSets(*(tuple(config[k]) for k in ("train", "validation", "test")))
    summary = {"status": "running", "baseline": [], "search": {}, "test": [], "gates": {}}

    def save():
        summary["budget"] = client.budget.read()
        (directory / "progress.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    try:
        for task_id in splits.train:
            target = directory / "baseline" / task_id
            if resume and target.exists():
                score, info, result, prompt, _ = client.read_task(seed, task_id, "baseline", target)
            else:
                score, info, result, prompt, _ = client.task(seed, task_id, "baseline", target)
            if (target / "semantic/analysis.json").exists():
                diagnostic = read(target / "semantic/analysis.json")
            else:
                diagnostic = client.semantic_feedback(
                    result, prompt, target, {"id": task_id, "split": "train"}
                )
            client.pool[task_id] = {
                "reward": score,
                "termination_reason": info["termination_reason"],
                "diagnostic": diagnostic,
            }
            summary["baseline"].append({"task_id": task_id, **client.pool[task_id]})
            save()
        write_json(directory / "failure_pool.json", client.pool)
        summary["baseline_semantic_candidates"] = any(
            x["reward"] < 1
            and any(d["category"] != "unknown" for d in x["diagnostic"]["diagnostics"])
            for x in client.pool.values()
        )
        summary["gates"]["A"] = False
        if not any(x["reward"] < 1 for x in client.pool.values()):
            raise ValueError(
                "No real training failure; expand the permitted Train coverage, do not invent one"
            )
        basic = run_search(client, "basic", seed, splits)
        summary["search"]["basic"] = basic["summary"]
        save()
        structured = run_search(client, "structured", seed, splits)
        summary["search"]["structured"] = structured["summary"]
        reflection_files = sorted((directory / "structured").glob("reflection-*/input.json"))
        # Inspect the actual official Reflection request, not intended evaluator output.
        consumed = []
        for p in reflection_files:
            content = read(p)
            text = content if isinstance(content, str) else json.dumps(content)
            if (
                "structured_feedback" in text
                and "diagnostics" in text
                and re.search(r"official_reward\s+0(?:\.0)?\b", text)
            ):
                consumed.append(str(p.relative_to(directory)))
        summary["gates"]["B"] = False
        summary["reflection_failure_evidence"] = consumed
        summary["gates"]["C"] = all(
            s["summary"]["new_candidates_evaluated"] >= 2
            and len(s["summary"]["train_tasks_observed"]) >= 3
            and s["summary"]["best_complete_validation"]
            for s in (basic, structured)
        )
        proof = algorithm_evidence(directory)
        summary["gates"].update(A=True, B=True)
        if not (directory / "algorithm_acceptance.json").exists():
            write_json(directory / "algorithm_acceptance.json", proof)
        save()
        if not all(summary["gates"].values()):
            raise ValueError("Real semantic/search gates unproven; preserve evidence before Test")
        prompts = {"baseline": seed, "basic": basic["best"], "structured": structured["best"]}
        write_json(
            directory / "frozen_test_prompts.json",
            {k: {"instruction": v, "sha256": digest(v)} for k, v in prompts.items()},
        )
        distinct = {}
        for arm, text in prompts.items():
            distinct.setdefault(digest(text), {"instruction": text, "arms": []})["arms"].append(arm)
        summary["test_plan"] = {
            "ids": list(splits.test),
            "trials": config["trials"],
            "unique_prompts": len(distinct),
            "identical_arms_share_measurement": True,
        }
        save()
        for task_id in splits.test:
            for trial in range(config["trials"]):
                client.trial_seed = config["seed"] + 10000 + trial
                for entry in distinct.values():
                    arm = entry["arms"][0]
                    target = directory / "test" / f"{task_id}-{arm}-{trial + 1}"
                    score, info, result, _, _ = client.task(
                        entry["instruction"], task_id, "test", target
                    )
                    summary["test"].append(
                        {
                            "task_id": task_id,
                            "trial": trial + 1,
                            "seed": client.trial_seed,
                            "arm": arm,
                            "aliases": entry["arms"],
                            "score": score,
                            "termination_reason": info["termination_reason"],
                            "trace": str(target.relative_to(directory)),
                            "candidate_sha256": result["prompt_sha256"],
                        }
                    )
                    save()
        summary["status"] = "complete"
    except Exception as exc:
        summary.update(status="stopped", error_type=type(exc).__name__)
        # Safe local diagnostics; no raw provider exception or secret-bearing config.
        if isinstance(exc, ValueError):
            summary["gate_error"] = str(exc)[:200]
    finally:
        save()
        write_json(directory / ("summary_recovered.json" if resume else "summary.json"), summary)
    return {
        "status": summary["status"],
        "artifacts": str(directory),
        "requests": summary["budget"]["requests"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="One baseline diagnostic-timeout recovery; never rerun a task",
    )
    args = parser.parse_args()
    try:
        result = run(load(args.config), live=args.live, resume=args.resume)
    except Exception as exc:
        print(json.dumps({"status": "stopped", "error_type": type(exc).__name__}))
        return 2
    print(json.dumps(result))
    return 0 if result["status"] in {"complete", "offline_config_only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
