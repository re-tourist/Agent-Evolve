"""Small M2-A runner: fixtures or pinned official Retail, with live execution closed."""

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import re
import subprocess
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

TAU_SHA = "da0835f6c67baef58bdda18f2a3b037dfb3a1754"


class LiveNotApprovedError(PermissionError):
    """M2-A intentionally has no switch that authorizes paid execution."""


class SimulatorError(RuntimeError):
    """User simulator failure, separate from an Agent business failure."""


class ProviderError(ConnectionError):
    """Provider API/transport failure; never an official business failure."""


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


@dataclass(frozen=True)
class Prompt:
    instruction: str
    policy: str

    @property
    def system(self) -> str:
        return (
            f"<instructions>\n{self.instruction}\n</instructions>\n"
            f"<policy>\n{self.policy}\n</policy>"
        )

    def record(self) -> dict:
        return {
            "instruction": self.instruction,
            "instruction_sha256": digest(self.instruction),
            "policy": self.policy,
            "policy_sha256": digest(self.policy),
            "system": self.system,
            "system_sha256": digest(self.system),
        }


@dataclass(frozen=True)
class Config:
    mode: str
    backend: str
    task_ids: tuple[str, ...]
    instruction: str
    output_dir: str
    run_id: str
    agent_model: str = "mock/agent"
    user_model: str = "mock/user"
    agent_args: dict | None = None
    user_args: dict | None = None
    num_tasks: int = 1
    seed: int = 42
    max_steps: int = 12
    domain: str = "retail"
    tau_checkout: str | None = None

    def __post_init__(self):
        if self.mode not in {"offline", "mock", "live"} or self.backend not in {"fixture", "tau"}:
            raise ValueError("Invalid mode or backend")
        if self.domain != "retail":
            raise ValueError("M2-A supports Retail text only")
        if not isinstance(self.instruction, str) or not self.instruction.strip():
            raise ValueError("Nonempty Agent Instruction required")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", self.run_id):
            raise ValueError("run_id must be a safe single directory name")
        if not isinstance(self.task_ids, tuple) or not self.task_ids:
            raise ValueError("task_ids must be a nonempty tuple")
        if len(set(self.task_ids)) != len(self.task_ids):
            raise ValueError("Explicit nonempty unique task_ids required")
        if any(
            not isinstance(t, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", t) for t in self.task_ids
        ):
            raise ValueError("Invalid task ID")
        for value, low, high in [
            (self.num_tasks, 1, 10),
            (self.seed, 0, 2**32 - 1),
            (self.max_steps, 2, 50),
        ]:
            if type(value) is not int or not low <= value <= high:
                raise ValueError("Invalid count, seed or step limit")
        if self.num_tasks != len(self.task_ids):
            raise ValueError(
                "num_tasks must equal the explicit task ID count; no silent truncation"
            )
        for model in (self.agent_model, self.user_model):
            if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9_./:-]+", model):
                raise ValueError("Invalid model identifier")
        for args in (self.agent_args, self.user_args):
            args = {} if args is None else args
            if not isinstance(args, dict) or set(args) - {
                "temperature",
                "max_tokens",
                "top_p",
                "timeout",
                "num_retries",
            }:
                raise ValueError(
                    "Only allowlisted generation parameters; never keys/URLs in config"
                )
            for key, value in args.items():
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise ValueError("Generation parameters must be finite numbers")
                if key in {"max_tokens", "num_retries"} and type(value) is not int:
                    raise ValueError("Token/retry limits must be integers")
                limits = {
                    "temperature": (0, 2),
                    "top_p": (0, 1),
                    "max_tokens": (1, 4096),
                    "timeout": (1, 120),
                    "num_retries": (0, 0),
                }
                if not limits[key][0] <= value <= limits[key][1]:
                    raise ValueError("Generation parameter out of bounds")

    @classmethod
    def load(cls, filename: Path):
        data = json.loads(filename.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Config must be a JSON object")
        if "instruction_file" in data:
            if "instruction" in data:
                raise ValueError("Choose instruction or instruction_file, not both")
            data["instruction"] = (filename.parent / data.pop("instruction_file")).read_text(
                encoding="utf-8"
            )
        for key in ("output_dir", "tau_checkout"):
            if data.get(key):
                data[key] = str((filename.parent / data[key]).resolve())
        if not isinstance(data.get("task_ids"), list):
            raise ValueError("task_ids must be a JSON list")
        data["task_ids"] = tuple(data["task_ids"])
        return cls(**data)


@contextmanager
def deny_network():
    """CLI runs sequentially; block socket attempts including upstream import-time fetches."""

    def denied(*args, **kwargs):
        raise PermissionError("Network prohibited in M2-A offline/mock execution")

    with (
        patch("socket.socket.connect", denied),
        patch("socket.socket.connect_ex", denied),
        patch("socket.create_connection", denied),
        patch("socket.getaddrinfo", denied),
        patch.dict(
            "os.environ", {"LITELLM_LOCAL_MODEL_COST_MAP": "True", "PYTHON_DOTENV_DISABLED": "1"}
        ),
    ):
        yield


def normalize(raw: dict) -> dict:
    """Keep upstream reward/details intact; never convert infrastructure errors to task failure."""
    reason = raw.get("termination_reason")
    errors = {
        "infrastructure_error": "infrastructure_error",
        "timeout": "infrastructure_error",
        "context_window_exceeded": "infrastructure_error",
        "user_error": "simulator_error",
        "agent_error": "agent_protocol_error",
        "unexpected_error": "runner_error",
        "max_steps": "step_limit",
    }
    reward_info = raw.get("reward_info")
    reward = reward_info.get("reward") if isinstance(reward_info, dict) else None
    if reward is not None and (type(reward) not in (int, float) or not math.isfinite(reward)):
        raise ValueError("Invalid official reward")
    error = errors.get(reason)
    excluded = error is not None
    score = None if excluded else reward
    status = error or (
        "task_success"
        if score == 1
        else "task_failure"
        if score is not None
        else "score_unavailable"
    )
    # Upstream get_cost sums absent message costs as zero. That is not provider evidence.
    messages = raw.get("messages") or []
    costs = {}
    for role, message_role in (("agent", "assistant"), ("user", "user")):
        participant_messages = [m for m in messages if m.get("role") == message_role]
        costs[role] = (
            sum(m["cost"] for m in participant_messages)
            if participant_messages and all(m.get("cost") is not None for m in participant_messages)
            else None
        )
    return {
        "status": status,
        "termination_reason": reason,
        "official_task_reward": score,
        "reward_availability": "available" if score is not None else "unavailable",
        "evaluation_details": reward_info,
        "excluded_from_task_metrics": excluded or score is None,
        "messages": raw.get("messages") or [],
        "usage": {role: raw.get(f"{role}_usage") for role in ("agent", "user")},
        "usage_availability": "per_message_if_present; missing fields unavailable",
        "provider_cost": costs,
        "cost_availability": "message estimates only when complete; supplier bill unavailable",
        "latency_seconds": raw.get("duration"),
        "error": {"type": error, "message": "See termination_reason; provider message unavailable"}
        if error
        else None,
    }


class FixtureBackend:
    """Synthetic fixture only; deliberately not an implementation of Retail scoring."""

    policy = "SYNTHETIC FIXTURE POLICY: require confirmation before modifying an order."

    def tasks(self, ids):
        known = {"fixture-retail-001", "fixture-retail-002"}
        if set(ids) - known:
            raise ValueError("Unknown fixture ID; official IDs require backend=tau")
        return [{"id": t, "provenance": "synthetic_fixture"} for t in ids]

    def run(self, task, config, prompt):
        # Fresh mutable state and history per invocation, not shared across tasks/trials.
        order = {"status": "pending"}
        messages = [
            {"role": "user", "content": "Please inspect my fixture order."},
            {
                "role": "assistant",
                "tool_calls": [
                    {"id": "fixture-call", "name": "inspect", "arguments": {"order_id": task["id"]}}
                ],
            },
            {"role": "tool", "id": "fixture-call", "content": dict(order)},
            {"role": "assistant", "content": "The order is pending."},
        ]
        order["status"] = "fixture-local-change"
        return {"messages": messages, "termination_reason": "user_stop", "reward_info": None}


def write_json(path: Path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def git_info() -> dict:
    result = {}
    for key, args in [("commit", ["rev-parse", "HEAD"]), ("dirty", ["status", "--porcelain"])]:
        try:
            p = subprocess.run(["git", *args], capture_output=True, text=True, timeout=5)
            result[key] = bool(p.stdout.strip()) if key == "dirty" else p.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            result[key] = "unavailable"
    return result


def execute(config: Config, *, backend=None, invocation=None) -> Path:
    # No config field, CLI flag, env variable or injected backend bypasses this gate.
    if config.mode == "live":
        raise LiveNotApprovedError("M2-A: live disabled pending explicit M2-B approval/review")
    with deny_network():
        if backend is None:
            if config.backend == "tau":
                from agent_evolve.tau_backend import TauBackend

                backend = TauBackend(config.tau_checkout)
            else:
                backend = FixtureBackend()
        tasks = backend.tasks(config.task_ids)
        if [t["id"] for t in tasks] != list(config.task_ids):
            raise ValueError("Backend task selection must match requested order and IDs")
        prompt = Prompt(config.instruction, backend.policy)
        directory = Path(config.output_dir) / config.run_id
        directory.mkdir(parents=True, exist_ok=False)
        config_record = asdict(config)
        write_json(directory / "config.json", config_record)
        write_json(directory / "prompt.json", prompt.record())
        metadata = {
            "schema_version": 1,
            "run_id": config.run_id,
            "mode": config.mode,
            "backend": config.backend,
            "created_utc": datetime.now(UTC).isoformat(),
            "git": git_info(),
            "invocation": invocation or "programmatic execute(Config); see config.json",
            "environment": {
                "python": platform.python_version(),
                "system": platform.system(),
                "machine": platform.machine(),
            },
            "packages": {
                name: importlib.metadata.version(name)
                for name in (
                    "agent-evolve",
                    *(["tau2", "litellm"] if config.backend == "tau" else []),
                )
            },
            "config_sha256": digest(canonical(config_record)),
            "upstream_sha": TAU_SHA if config.backend == "tau" else "unavailable",
            "data_identity": getattr(backend, "data_identity", "synthetic_fixture"),
            "trials": 1,
            "seed": config.seed,
            "model_calls": 0,
            "model_execution": "none; offline/scripted participants",
            "prompt_sha256": digest(prompt.instruction),
            "policy_sha256": digest(prompt.policy),
        }
        write_json(directory / "metadata.json", metadata)
        summaries = []
        for task in tasks:
            start = time.monotonic()
            result = {
                "task_id": task["id"],
                "task_sha256": digest(canonical(task)),
                "mode": config.mode,
                "model_execution": "none; offline/scripted participants",
                "backend": config.backend,
                "seed": config.seed,
                "prompt_sha256": digest(prompt.instruction),
                "models": {"agent": config.agent_model, "user": config.user_model},
                "generation_parameters": {"agent": config.agent_args, "user": config.user_args},
            }
            try:
                raw = {} if config.mode == "offline" else backend.run(task, config, prompt)
                result.update(normalize(raw))
                if config.mode == "offline":
                    result["status"] = "preflight_only"
                result["reward_source"] = (
                    "official_evaluator_on_scripted_trace"
                    if config.backend == "tau" and raw
                    else "unavailable; no official evaluation"
                )
                write_json(directory / f"{task['id']}.raw.json", raw)
            except Exception as exc:
                # Persist a safe exception class, not provider messages/headers/credentials.
                category = (
                    "simulator_error"
                    if isinstance(exc, SimulatorError)
                    else ("infrastructure_error" if isinstance(exc, OSError) else "runner_error")
                )
                result.update(normalize({"termination_reason": "unexpected_error"}))
                result.update(
                    status=category,
                    error={
                        "type": type(exc).__name__,
                        "message": f"{category}; exception text withheld to protect secrets",
                    },
                )
            result["wall_seconds"] = time.monotonic() - start
            write_json(directory / f"{task['id']}.json", result)
            summaries.append(
                {
                    k: result[k]
                    for k in (
                        "task_id",
                        "status",
                        "official_task_reward",
                        "excluded_from_task_metrics",
                    )
                }
            )
        write_json(
            directory / "summary.json",
            {"mode": config.mode, "results": summaries, "benchmark_performance_claim": False},
        )
        return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = Config.load(args.config)
        directory = execute(
            config,
            invocation=["python", "-m", "agent_evolve.baseline", "--config", str(args.config)],
        )
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"{type(exc).__name__}: {exc}\n")
    print(f"Artifacts: {directory}")
    # Fail the command when infrastructure/simulator errors occurred, while retaining artifacts.
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    errors = {
        "runner_error",
        "infrastructure_error",
        "simulator_error",
        "agent_protocol_error",
        "step_limit",
    }
    if config.backend == "tau" and config.mode == "mock":
        errors.add("score_unavailable")
    if any(r["status"] in errors for r in summary["results"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
