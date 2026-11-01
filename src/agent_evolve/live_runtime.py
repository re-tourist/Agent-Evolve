"""Serial, file-backed budget for this bounded Qwen experiment, not a billing service."""

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import time
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from agent_evolve.baseline import ProviderError, write_json
from agent_evolve.qwen_smoke import MODEL, Calls

ROLE = ContextVar("qwen_role", default=None)
PHASE_LIMITS = {"basic": 92, "structured": 92, "test": 216}


class StageBudget(RuntimeError):
    """Cannot admit another whole task without using another stage's reserve."""


def credentials(directory):
    files = list(Path(directory).glob("*.csv"))
    if len(files) != 1:
        raise ValueError("Expected one local credential CSV")
    source = files[0].resolve()
    root = Path(__file__).resolve().parents[2]
    relative = source.relative_to(root)
    if subprocess.check_output(["git", "ls-files", "--", str(relative)], cwd=root).strip():
        raise ValueError("Credential CSV tracked")
    if subprocess.check_output(
        ["git", "log", "--all", "--format=%H", "--", str(relative)], cwd=root
    ).strip():
        raise ValueError("Credential CSV in history")
    subprocess.run(["git", "check-ignore", "-q", str(relative)], cwd=root, check=True)
    raw = source.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("gb18030")
    cells = list(csv.reader(io.StringIO(text)))

    def norm(value):
        return re.sub(r"[\s_-]", "", value).lower()

    if all(len(row) == 2 for row in cells) and any(norm(r[0]) == "apikey" for r in cells):
        rows = [dict(cells)]
    else:
        rows = list(csv.DictReader(io.StringIO(text)))
    keys = [v.strip() for row in rows for k, v in row.items() if norm(k) == "apikey"]
    urls = [v.strip() for row in rows for k, v in row.items() if norm(k) == "openaicompatible"]
    if len(keys) != 1 or not keys[0].startswith("sk-") or any(c.isspace() for c in keys[0]):
        raise ValueError("Credential field unavailable")
    if len(urls) != 1:
        raise ValueError("CSV endpoint unavailable")
    url = urlsplit(urls[0])
    if (
        url.scheme != "https"
        or url.username
        or url.password
        or url.query
        or url.fragment
        or not re.fullmatch(r"[a-z0-9-]+\.cn-beijing\.maas\.aliyuncs\.com", url.hostname or "")
        or url.path != "/compatible-mode/v1"
    ):
        raise ValueError("Only the approved Beijing workspace endpoint is allowed")
    return keys[0], urls[0]


def estimate_rmb(input_tokens, output_tokens):
    if input_tokens <= 128_000:
        a, b = 0.8, 2
    elif input_tokens <= 256_000:
        a, b = 2.4, 20
    else:
        a, b = 4.8, 48
    return (input_tokens * a + output_tokens * b) / 1_000_000


class Budget:
    def __init__(self, filename):
        self.path = Path(filename)

    @classmethod
    def carry_forward(cls, filename, predecessor, *, phase_limits, task_calls=48):
        """One serial successor, retaining cumulative occupancy and immutable old stop."""
        predecessor = Path(predecessor).resolve()
        raw = predecessor.read_bytes()
        old = json.loads(raw)
        if old["pending"] is not None or not old["stopped"]:
            raise ValueError("Predecessor must be terminal with no pending request")
        if old["limit"] != 5000 or old["cost_limit_rmb"] != 50:
            raise ValueError("Cumulative authorization differs")
        if old["requests"] >= 5000 or old["cost_rmb"] >= 50:
            raise ProviderError("Cumulative allowance exhausted")
        if Path(filename).exists():
            raise FileExistsError("Successor already exists")
        # Exclusive marker prevents branching one authorization into multiple budgets.
        marker = predecessor.parent / "budget-successor.json"
        with marker.open("x", encoding="utf-8") as stream:
            json.dump(
                {
                    "successor": str(Path(filename).resolve()),
                    "predecessor_sha256": hashlib.sha256(raw).hexdigest(),
                },
                stream,
            )
        budget = cls.create(
            filename,
            limit=5000,
            cost_limit_rmb=50,
            phase_limits=phase_limits,
            task_calls=task_calls,
        )
        state = budget.read()
        for key in (
            "requests",
            "cost_rmb",
            "input_tokens",
            "output_tokens",
            "unknown_usage_requests",
            "unknown_cost_reserve_rmb",
        ):
            if key in old:
                state[key] = old[key]
        state["predecessor"] = {
            "path": str(predecessor),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "snapshot": old,
        }
        budget.save(state)
        budget.log(
            {
                "status": "carry_forward",
                "requests": old["requests"],
                "cost_rmb": old["cost_rmb"],
                "predecessor_sha256": state["predecessor"]["sha256"],
            }
        )
        return budget

    @classmethod
    def create(cls, filename, *, limit=400, cost_limit_rmb=30, phase_limits=None, task_calls=24):
        if not 1 <= limit <= 5000 or not 0 < cost_limit_rmb <= 50 or not 1 <= task_calls <= 64:
            raise ValueError("Budget exceeds approved bounds")
        phase_limits = dict(PHASE_LIMITS if phase_limits is None else phase_limits)
        if not phase_limits or any(
            type(v) is not int or not 1 <= v <= limit for v in phase_limits.values()
        ):
            raise ValueError("Invalid phase limits")
        write_json(
            Path(filename),
            {
                "limit": limit,
                "cost_limit_rmb": cost_limit_rmb,
                "phase_limits": phase_limits,
                "task_calls": task_calls,
                "requests": 0,
                "cost_rmb": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "phases": dict.fromkeys(phase_limits, 0),
                "stopped": None,
                "pending": None,
            },
        )
        return cls(filename)

    def read(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        # Windows file watchers can briefly hold a new JSON file. Retry only this
        # atomic local rename, never a model request or task, and fail closed.
        for delay in (0.02, 0.05, 0.1, None):
            try:
                os.replace(temporary, self.path)
                break
            except PermissionError:
                if delay is None:
                    raise
                time.sleep(delay)

    def stop(self, reason):
        state = self.read()
        state["stopped"] = state["stopped"] or reason
        self.save(state)

    def admit_task(self, phase):
        state = self.read()
        if state["stopped"] or state["pending"]:
            raise ProviderError("Global budget is stopped or unresolved")
        if min(
            state["limit"] - state["requests"],
            state.get("phase_limits", PHASE_LIMITS)[phase] - state["phases"][phase],
        ) < state.get("task_calls", 24):
            raise StageBudget("Insufficient whole-task admission reserve")

    def begin(self, phase, role, association):
        state = self.read()
        if (
            state["stopped"]
            or state["pending"]
            or state["requests"] >= state["limit"]
            or state["cost_rmb"] >= state["cost_limit_rmb"]
            or role not in {"agent", "simulator", "reflection", "diagnostic"}
        ):
            self.stop("global_limit_or_invalid_role")
            raise ProviderError("Global request admission stopped")
        if state["phases"][phase] >= state.get("phase_limits", PHASE_LIMITS)[phase]:
            raise StageBudget("Stage reserve exhausted")
        state["requests"] += 1
        state["phases"][phase] += 1
        event = {
            "request": state["requests"],
            "phase": phase,
            "role": role,
            "association": association,
            "status": "admitted",
            "time": time.time(),
        }
        state["pending"] = event
        self.save(state)
        self.log(event)
        return event

    def log(self, event):
        with self.path.with_suffix(".jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")

    def finish(self, event, response=None, error=None, seconds=0, status_code=None):
        state = self.read()
        if state["pending"] != event:
            raise ProviderError("Budget state mismatch")
        record = dict(event, seconds=seconds)
        usage = response.get("usage") if response is not None else None
        if usage is not None:
            usage = usage.model_dump(mode="json") if hasattr(usage, "model_dump") else dict(usage)
        if (
            error
            or not usage
            or any(
                type(usage.get(k)) is not int or usage[k] < 0
                for k in ("prompt_tokens", "completion_tokens")
            )
        ):
            record.update(status="error", error_type=error or "UsageUnavailable")
            record["http_status"] = status_code if type(status_code) is int else "unavailable"
            state["stopped"] = error or "usage_unavailable"
        else:
            amount = estimate_rmb(usage["prompt_tokens"], usage["completion_tokens"])
            record.update(
                status="returned", usage=usage, estimated_rmb=amount, response_id=response.get("id")
            )
            state["cost_rmb"] += amount
            state["input_tokens"] += usage["prompt_tokens"]
            state["output_tokens"] += usage["completion_tokens"]
            if state["cost_rmb"] >= 30:
                state["stopped"] = "cost_limit"
        state["pending"] = None
        self.save(state)
        self.log(record)
        if record["status"] == "error":
            raise ProviderError("Provider/usage failure; global requests stopped")


@contextmanager
def shared_calls(
    directory,
    key,
    budget_file,
    phase,
    association,
    *,
    reflection=False,
    limit=24,
    seconds=600,
    max_tokens=1024,
    request_seconds=30,
):
    from tau2.agent import llm_agent
    from tau2.user import user_simulator
    from tau2.utils import llm_utils

    budget = Budget(budget_file)
    original = llm_utils.completion
    repeated = []

    def completion(**kwargs):
        if kwargs.get("model") != MODEL:
            budget.stop("unexpected_model")
            raise ProviderError("Unexpected model refused")
        event = budget.begin(phase, ROLE.get(), association)
        start = time.monotonic()
        try:
            response = original(**kwargs)
        except Exception as exc:
            budget.finish(
                event,
                error=type(exc).__name__,
                seconds=time.monotonic() - start,
                status_code=getattr(exc, "status_code", None),
            )
            raise AssertionError("unreachable") from None
        if (response.get("model") or "").removeprefix("openai/") != MODEL.removeprefix("openai/"):
            budget.finish(event, error="UnexpectedResponseModel", seconds=time.monotonic() - start)
        budget.finish(event, response=response, seconds=time.monotonic() - start)
        write_json(Path(directory) / f"response-{event['request']:04d}.json", response.to_dict())
        if ROLE.get() == "agent":
            tool_calls = response.choices[0].message.tool_calls
            signature = [(tc.function.name, tc.function.arguments) for tc in tool_calls or []]
            # Include last tool result: state-changing repeat calls are not conflated.
            last = next(
                (
                    m.get("content")
                    for m in reversed(kwargs.get("messages", []))
                    if m.get("role") == "tool"
                ),
                None,
            )
            repeated.append((signature, last))
            if signature and len(repeated) >= 3 and repeated[-1] == repeated[-2] == repeated[-3]:
                budget.stop("repeated_tool_loop")
                raise ProviderError("Repeated unchanged tool loop")
        return response

    def labelled(function, role):
        def generate(*args, **kwargs):
            token = ROLE.set(role)
            try:
                return function(*args, **kwargs)
            finally:
                ROLE.reset(token)

        return generate

    calls = Calls(
        completion,
        key,
        Path(directory),
        limit=1 if reflection else limit,
        seconds=seconds,
        max_tokens=max_tokens,
        request_seconds=request_seconds,
    )
    try:
        with (
            patch.object(llm_utils, "completion", calls),
            patch.object(llm_utils, "get_response_cost", lambda response: None),
            patch.object(llm_agent, "generate", labelled(llm_agent.generate, "agent")),
            patch.object(
                user_simulator, "generate", labelled(user_simulator.generate, "simulator")
            ),
        ):
            yield calls
    finally:
        if calls.failed and not budget.read()["stopped"]:
            budget.stop("local_call_or_time_limit")
