"""One Retail task / one trial. Default preflight is offline; Live needs explicit opt-in."""

import argparse
import hashlib
import os
import time
from contextlib import contextmanager
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from agent_evolve.baseline import (
    TAU_SHA,
    Config,
    LiveNotApprovedError,
    Prompt,
    ProviderError,
    canonical,
    deny_network,
    digest,
    git_info,
    normalize,
    write_json,
)

MODEL = "openai/qwen-plus-2025-12-01"
BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ROOT = Path(__file__).resolve().parents[2]


class CallLimit(ProviderError):
    """Call/time admission failed; no zero task reward."""


class Calls:
    """Serial total-call guard for Agent and Simulator; no retry after any fault."""

    def __init__(self, completion, key, path, *, limit=24, seconds=600):
        self.completion, self.key, self.path = completion, key, path
        self.limit, self.deadline = limit, time.monotonic() + seconds
        self.count, self.failed = 0, False

    def __call__(self, **kwargs):
        if self.failed or self.count >= self.limit or time.monotonic() >= self.deadline:
            self.failed = True
            raise CallLimit("Single-task call/time limit reached or prior provider fault")
        if kwargs.get("model") != MODEL:
            self.failed = True
            raise ProviderError("Unexpected model/Judge refused")
        self.count += 1
        start = time.monotonic()
        record = {"call": self.count, "model": MODEL, "status": "started"}
        kwargs.update(
            api_key=self.key,
            api_base=BASE,
            timeout=30,
            num_retries=0,
            max_retries=0,
            max_tokens=1024,
            temperature=0,
            extra_body={"enable_thinking": False},
            caching=False,
        )
        try:
            response = self.completion(**kwargs)
            record.update(status="returned", usage=response.get("usage"))
            if record["usage"] is not None:
                usage = record["usage"]
                record["usage"] = (
                    usage.model_dump(mode="json") if hasattr(usage, "model_dump") else dict(usage)
                )
            return response
        except Exception:
            self.failed = True
            record.update(status="provider_error")
            raise ProviderError("Qwen request failed; raw exception withheld") from None
        finally:
            record["seconds"] = time.monotonic() - start
            write_json(self.path / f"call-{self.count:03d}.json", record)


@contextmanager
def qwen_calls(directory, key):
    from tau2.utils import llm_utils

    calls = Calls(llm_utils.completion, key, directory)
    # Credential injection happens AFTER upstream request-log construction.
    # Upstream logs therefore cannot serialize the API key into request kwargs.
    with (
        patch.object(llm_utils, "completion", calls),
        patch.object(llm_utils, "get_response_cost", lambda response: None),
    ):
        yield calls


def run(run_id, *, live=False, approved=False):
    if live and not approved:
        raise LiveNotApprovedError("Explicit --approve-single-task required after user approval")
    config = Config(
        mode="live",
        backend="tau",
        task_ids=("0",),
        instruction=(ROOT / "examples/m2/instruction.txt").read_text(encoding="utf-8"),
        output_dir=str(ROOT / "runs/qwen"),
        run_id=run_id,
        tau_checkout=str(ROOT / ".cache/tau2-source"),
        agent_model=MODEL,
        user_model=MODEL,
        max_steps=32,
        agent_args={"max_tokens": 1024, "timeout": 30, "num_retries": 0, "temperature": 0},
        user_args={"max_tokens": 1024, "timeout": 30, "num_retries": 0, "temperature": 0},
    )
    return execute_task(config, live=live, approved=approved)


def execute_task(config, *, live=False, approved=False, call_context=None):
    """Reusable official one-task execution; caller supplies only a bounded call context."""
    if live and not approved:
        raise LiveNotApprovedError("Explicit Live authorization required")
    if config.backend != "tau" or len(config.task_ids) != 1:
        raise ValueError("One official Retail task required")
    task_id = config.task_ids[0]
    with deny_network():
        from agent_evolve.tau_backend import TauBackend, build_live_components

        backend = TauBackend(config.tau_checkout)
        task = backend.tasks((task_id,))[0]
        criteria = task.get("evaluation_criteria") or {}
        if criteria.get("nl_assertions") or "COMMUNICATE" in criteria.get("reward_basis", []):
            raise ValueError("Task requires a Judge; stop and review, preserve official scoring")
        prompt = Prompt(config.instruction, backend.policy)
        orchestrator = build_live_components(config, task, prompt)
        # Render both prompts now, before credentials/network; detects missing official data.
        orchestrator.agent.get_init_state()
        orchestrator.user.get_init_state()
    if not live:
        return {"status": "offline_preflight", "task": task_id, "trials": 1, "model_calls": 0}
    key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if not key:
        raise ValueError("Set DASHSCOPE_API_KEY in the process environment")
    directory = Path(config.output_dir) / config.run_id
    directory.mkdir(parents=True, exist_ok=False)
    write_json(directory / "config.json", asdict(config))
    write_json(directory / "prompt.json", prompt.record())
    write_json(directory / "task.json", task)
    write_json(
        directory / "metadata.json",
        {
            "git": git_info(),
            "created_utc": datetime.now(UTC).isoformat(),
            "mode": "real_api",
            "trials": 1,
            "task_id": task_id,
            "upstream_sha": TAU_SHA,
            "data_identity": backend.data_identity,
            "tools_sha256": digest(
                canonical([t.openai_schema for t in orchestrator.environment.get_tools()])
            ),
            "language_pack_sha256": hashlib.sha256(
                (Path(config.tau_checkout) / "data/tau2/multilingual/en/pack.yaml").read_bytes()
            ).hexdigest(),
            "task_sha256": digest(canonical(task)),
            "model": MODEL,
            "base_url": BASE,
            "judge": "none",
            "reflection": "not invoked",
            "limits": {
                "calls": 24,
                "steps": 32,
                "request_seconds": 30,
                "admission_seconds": 600,
                "output_tokens_per_call": 1024,
            },
        },
    )
    from tau2.runner import run_simulation

    with (call_context or qwen_calls)(directory, key) as calls:
        raw = {}
        try:
            raw = run_simulation(orchestrator).model_dump(mode="json")
            write_json(directory / f"{task_id}.raw.json", raw)
            result = normalize(raw)
            if calls.failed:
                result.update(
                    status="infrastructure_error",
                    official_task_reward=None,
                    excluded_from_task_metrics=True,
                )
        except Exception as exc:
            result = normalize({"termination_reason": "infrastructure_error"})
            result["error"] = {"type": type(exc).__name__, "message": "Details withheld"}
        result.update(
            mode="real_api",
            task_id=task_id,
            backend="tau",
            prompt_sha256=digest(prompt.instruction),
            official_raw_reward=(raw.get("reward_info") or {}).get("reward"),
            model_calls=calls.count,
            reward_source="official_evaluator"
            if result["official_task_reward"] is not None
            else "unavailable",
        )
        write_json(directory / f"{task_id}.json", result)
        # Observed order IDs only; no hidden target or whole-dataset DB export.
        order_ids = {
            call.get("arguments", {}).get("order_id")
            for message in raw.get("messages", [])
            for call in message.get("tool_calls") or []
        }
        write_json(
            directory / "final_state.json",
            {
                "orders": {
                    order_id: orchestrator.environment.tools.db.orders[order_id].model_dump(
                        mode="json"
                    )
                    for order_id in sorted(order_ids - {None})
                    if order_id in orchestrator.environment.tools.db.orders
                },
                "source": "actual environment after run; observed order IDs only",
            },
        )
        write_json(
            directory / "summary.json",
            {
                "status": result["status"],
                "model_calls": calls.count,
                "official_raw_reward": result["official_raw_reward"],
                "metric_note": "Smoke annotations never exclude official failures from benchmarks",
                "benchmark_performance_claim": False,
            },
        )
    return {"artifacts": str(directory), "status": result["status"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="qwen-task0-001")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--approve-single-task", action="store_true")
    args = parser.parse_args()
    try:
        result = run(args.run_id, live=args.live, approved=args.approve_single_task)
    except Exception as exc:
        parser.exit(2, f"{type(exc).__name__}: refused/aborted; no automatic retry\n")
    print(result)
    return 0 if result["status"] in {"offline_preflight", "task_success", "task_failure"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
