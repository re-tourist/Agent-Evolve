"""Conservative observations over normalized M2 traces; never a task scoring function."""

import json
import math
import re

ARGUMENT_ERROR = re.compile(
    r"^Error: [\w.<>]+\(\) (?:missing \d+ required (?:positional|keyword-only) "
    r"arguments?:|got an unexpected keyword argument )"
)
TERMINATIONS = {
    "user_stop",
    "agent_stop",
    "max_steps",
    "too_many_errors",
    "infrastructure_error",
    "timeout",
    "context_window_exceeded",
    "user_error",
    "agent_error",
    "unexpected_error",
}


def diagnose(result: dict) -> dict:
    """Read observations only. Returned JSON never copies content, gold details or targets.

    `certain` describes the reported observation, NOT its responsibility or causal
    relation to Reward. Pointers refer to this normalized result, using JSON Pointer.
    The caller must enforce split access; this pure function cannot infer data splits.
    """
    if not isinstance(result, dict) or not isinstance(result.get("messages", []), list):
        raise ValueError("Expected a normalized result with a messages list")
    diagnostics = []

    def add(kind, certain, explanation, *evidence):
        diagnostics.append(
            {
                "type": kind,
                "certain": certain,
                "explanation": explanation,
                "evidence": list(evidence),
            }
        )

    def ref(pointer, value):
        return {"pointer": pointer, "value": value}

    calls = {}
    for i, message in enumerate(result.get("messages") or []):
        if not isinstance(message, dict):
            raise ValueError("Expected normalized message objects")
        path = f"/messages/{i}"
        role = message.get("role")
        if role in {"assistant", "user"}:
            for j, call in enumerate(message.get("tool_calls") or []):
                call_path = f"{path}/tool_calls/{j}"
                key = (call.get("id"), role)
                if isinstance(call.get("id"), str) and call["id"]:
                    calls.setdefault(key, []).append(call_path)
                if "arguments" in call and not isinstance(call["arguments"], dict):
                    add(
                        "invalid_tool_arguments",
                        True,
                        "Recorded normalized tool arguments are not an object; "
                        "their origin is unknown.",
                        ref(
                            call_path + "/arguments",
                            {"observed_type": type(call["arguments"]).__name__},
                        ),
                    )
        if role != "tool" or message.get("error") is not True:
            continue
        rejected = message.get("execution_status") == "rejected"
        evidence = [ref(path + "/error", True)]
        if message.get("requestor") in {"assistant", "user"}:
            evidence.append(ref(path + "/requestor", message["requestor"]))
        if rejected:
            evidence.append(ref(path + "/execution_status", "rejected"))
        # Only associate a unique PRECEDING call with the same ID and requestor.
        matches = calls.get((message.get("id"), message.get("requestor")), [])
        if len(matches) == 1:
            evidence.append(ref(matches[0], {"association": "matching id and requestor"}))
        add(
            "tool_execution_error",
            True,
            "The framework rejected this call before execution; "
            "this is not an executed tool failure."
            if rejected
            else "The tool reports an error; cause, responsibility and effect on Reward "
            "are unknown.",
            *evidence,
        )
        content = message.get("content")
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                pass
        if (
            not rejected
            and len(matches) == 1
            and isinstance(content, str)
            and ARGUMENT_ERROR.match(content)
        ):
            add(
                "invalid_tool_arguments",
                True,
                "The tool reports a Python argument-binding error; "
                "no claim about business correctness.",
                ref(path + "/content", {"observed_marker": "python_argument_binding_error"}),
                ref(matches[0], {"association": "matching id and requestor"}),
            )

    reason = result.get("termination_reason")
    known = isinstance(reason, str) and reason in TERMINATIONS
    abnormal = known and reason not in {"user_stop", "agent_stop"}
    add(
        "task_completion",
        known,
        "The recorded run terminated abnormally; this does not establish an Agent business failure."
        if abnormal
        else "A participant stopped; early termination or business completion cannot be inferred."
        if known
        else "Termination evidence is unavailable; completion cannot be established.",
        ref(
            "/termination_reason" if "termination_reason" in result else "",
            reason if known else {"availability": "unavailable"},
        ),
    )
    reward = result.get("official_task_reward")
    if (
        result.get("excluded_from_task_metrics") is False
        and type(reward) in (int, float)
        and math.isfinite(reward)
        and 0 <= reward < 1
    ):
        add(
            "uncertain_failure",
            False,
            "Official Reward is below 1. Trace observations do not establish the cause; "
            "do not infer a required tool path.",
            ref("/official_task_reward", reward),
        )
    return {"schema_version": 1, "diagnostics": diagnostics}
