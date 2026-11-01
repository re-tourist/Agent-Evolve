"""Official Reward adapter and immutable candidate evidence; no scoring algorithm."""

import json
import math
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from agent_evolve.baseline import TAU_SHA, Config, digest, write_json


class EvaluationUnavailable(RuntimeError):
    """A failed/invalid evaluation cannot supply a score to optimization."""


class EvaluationLimit(RuntimeError):
    """Local admission guard reached; never converted into a zero task Reward."""


def candidate_text(candidate):
    if not isinstance(candidate, str) or not candidate.strip() or len(candidate) > 8192:
        raise ValueError("Candidate must be nonempty instruction text, at most 8192 characters")
    return candidate


@dataclass(frozen=True)
class TaskSets:
    train: tuple[str, ...]
    validation: tuple[str, ...]
    test: tuple[str, ...]
    tau_sha: str = TAU_SHA

    def __post_init__(self):
        seen = set()
        if self.tau_sha != TAU_SHA:
            raise ValueError("Task source SHA must match the pinned tau source")
        for group in (self.train, self.validation, self.test):
            if not isinstance(group, tuple) or not group:
                raise ValueError("Each split needs an explicit nonempty tuple")
            for task in group:
                if not isinstance(task, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", task):
                    raise ValueError("Invalid task ID")
                if task in seen:
                    raise ValueError("Duplicate/overlapping task IDs across splits")
                seen.add(task)

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if set(data) != {"train", "validation", "test", "tau_sha"}:
            raise ValueError("Split file contains only IDs and pinned source; no task answers")
        for key in ("train", "validation", "test"):
            if not isinstance(data[key], list):
                raise ValueError("Split IDs must be lists")
            data[key] = tuple(data[key])
        return cls(**data)

    def examples(self, split):
        if split not in {"train", "validation"}:
            raise ValueError("Test tasks must never be exposed to GEPA")
        return [{"id": task, "split": split} for task in getattr(self, split)]

    def check(self, example):
        if not isinstance(example, dict) or set(example) != {"id", "split"}:
            raise ValueError("Evaluator example must contain only id and split")
        if example not in self.examples(example["split"]):
            raise ValueError("Example is not in the declared optimization split")


class CandidateLedger:
    def __init__(self, directory):
        self.directory = Path(directory)
        (self.directory / "candidates").mkdir(exist_ok=False)
        (self.directory / "evaluations").mkdir(exist_ok=False)
        (self.directory / "evaluations.jsonl").touch(exist_ok=False)
        self.attempts = 0

    def candidate(self, text):
        candidate_text(text)
        sha = digest(text)
        path = self.directory / "candidates" / f"{sha}.json"
        if not path.exists():
            write_json(
                path,
                {
                    "sha256": sha,
                    "instruction": text,
                    "lineage": "unavailable in callback; see official candidate_pool.json",
                },
            )
        elif json.loads(path.read_text(encoding="utf-8"))["instruction"] != text:
            raise ValueError("Candidate evidence does not match its content hash")
        return sha

    def record(self, record):
        with (self.directory / "evaluations.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


def run_m2_worker(config: Config, directory: Path, python: Path, timeout: int):
    request = directory / "request.json"
    write_json(request, asdict(config))
    env = os.environ.copy()
    env.update(
        PYTHONIOENCODING="utf-8", PYTHON_DOTENV_DISABLED="1", LITELLM_LOCAL_MODEL_COST_MAP="True"
    )
    # No shell, model credentials or candidate text on the command line.
    command = [str(python), "-m", "agent_evolve.baseline", "--config", str(request)]
    try:
        process = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parents[2],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        write_json(directory / "worker.json", {"status": "timeout", "score": None})
        raise EvaluationUnavailable("Worker timeout; no task score admitted") from None
    write_json(
        directory / "worker.json",
        {
            "exit": process.returncode,
            "stderr_sha256": digest(process.stderr),
            "stdout": process.stdout,
        },
    )
    result_dir = Path(config.output_dir) / config.run_id
    if process.returncode != 0:
        raise EvaluationUnavailable("M2 worker failed; retained artifacts, no score admitted")

    def read(name):
        return json.loads((result_dir / name).read_text(encoding="utf-8"))

    return read(f"{config.task_ids[0]}.json"), read("prompt.json"), read("metadata.json")


class TauEvaluator:
    """GEPA callable (candidate, example) -> (official Reward, basic trace feedback)."""

    def __init__(self, baseline, splits, ledger, python, *, max_evals, timeout=90, worker=None):
        if baseline.mode != "mock" or baseline.backend != "tau":
            raise ValueError("M3-A uses only M2's scripted official tau backend")
        self.baseline, self.splits, self.ledger = baseline, splits, ledger
        self.python, self.max_evals, self.timeout = Path(python), max_evals, timeout
        self.worker = worker or run_m2_worker
        self.transport = "injected_test_worker" if worker else "official_m2_subprocess"
        self.policy_hash = None

    def __call__(self, candidate, example):
        candidate_text(candidate)
        self.splits.check(example)
        if self.ledger.attempts >= self.max_evals:
            raise EvaluationLimit("Evaluation admission budget exhausted")
        sha = self.ledger.candidate(candidate)
        self.ledger.attempts += 1
        sequence = self.ledger.attempts
        directory = self.ledger.directory / "evaluations" / f"{sequence:06d}"
        directory.mkdir(exist_ok=False)
        config = replace(
            self.baseline,
            instruction=candidate,
            task_ids=(example["id"],),
            num_tasks=1,
            output_dir=str(directory),
            run_id="m2",
        )
        event = {
            "sequence": sequence,
            "candidate_sha256": sha,
            "example": dict(example),
            "transport": self.transport,
            "score": None,
            "status": "started",
        }
        start = time.monotonic()
        try:
            result, prompt, metadata = self.worker(config, directory, self.python, self.timeout)
            if (
                result.get("task_id") != example["id"]
                or result.get("mode") != "mock"
                or result.get("backend") != "tau"
                or metadata.get("upstream_sha") != TAU_SHA
                or result.get("prompt_sha256") != sha
                or prompt.get("instruction_sha256") != sha
            ):
                raise EvaluationUnavailable("M2 result identity mismatch")
            policy_hash = prompt.get("policy_sha256")
            if not policy_hash or (
                self.policy_hash is not None and policy_hash != self.policy_hash
            ):
                raise EvaluationUnavailable("Policy changed across candidate evaluations")
            self.policy_hash = policy_hash
            score = result.get("official_task_reward")
            details = result.get("evaluation_details")
            if (
                result.get("excluded_from_task_metrics") is not False
                or result.get("status") not in {"task_success", "task_failure"}
                or result.get("reward_source") != "official_evaluator_on_scripted_trace"
                or type(score) not in (int, float)
                or not math.isfinite(score)
                or not 0 <= score <= 1
                or not isinstance(details, dict)
                or type(details.get("reward")) not in (int, float)
                or details["reward"] != score
            ):
                raise EvaluationUnavailable("Invalid/unavailable official task Reward")
            feedback = {
                "task_id": example["id"],
                "status": result["status"],
                "score_source": self.transport,
                "official_reward": score,
                "candidate_sha256": sha,
                "policy_sha256": policy_hash,
                "trace_path": str(directory.relative_to(self.ledger.directory) / "m2"),
                "termination_reason": result.get("termination_reason", "unavailable"),
                "message_count": len(result.get("messages") or []),
                "tool_names": [
                    call["name"]
                    for msg in result.get("messages", [])
                    for call in msg.get("tool_calls") or []
                ],
                "model_execution": "scripted; no real LLM",
                "usage": result.get("usage"),
            }
            event.update(score=score, feedback=feedback, status="scored")
            return float(score), feedback
        except Exception as exc:
            event.update(
                status="error",
                error_type=type(exc).__name__,
                trace_path=str(directory.relative_to(self.ledger.directory) / "m2"),
            )
            raise
        finally:
            event["seconds"] = time.monotonic() - start
            write_json(directory / "evaluation.json", event)
            self.ledger.record(event)
