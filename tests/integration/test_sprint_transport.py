"""Real pinned SDK, local mock HTTP; exercise the actual Reflection worker, no cloud."""

import json
import os

import pytest

from agent_evolve.baseline import deny_network
from agent_evolve.experiment import worker
from agent_evolve.live_runtime import Budget
from agent_evolve.qwen_smoke import MODEL

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_TESTS") != "1", reason="pinned tau only"
)


@pytest.mark.parametrize("kind", ["reflection", "diagnostic"])
def test_reflection_worker_guarded_real_sdk_transport(tmp_path, monkeypatch, kind):
    budget = Budget.create(tmp_path / "budget.json")
    directory = tmp_path / "reflection"
    directory.mkdir()
    with deny_network():
        import httpx
        import litellm
        from openai import OpenAI
        from tau2.utils import llm_utils

        requests = []

        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            assert body["enable_thinking"] is False and body["max_tokens"] == 1024
            return httpx.Response(
                200,
                json={
                    "id": "offline",
                    "object": "chat.completion",
                    "created": 1,
                    "model": MODEL.split("/")[1],
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {
                                "role": "assistant",
                                "content": "real SDK mock transport output",
                            },
                        }
                    ],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
                },
            )

        with httpx.Client(transport=httpx.MockTransport(handler)) as http:
            api = OpenAI(
                api_key="fake",
                base_url="https://offline.example/v1",
                http_client=http,
                max_retries=0,
            )
            monkeypatch.setattr(
                llm_utils, "completion", lambda **kwargs: litellm.completion(client=api, **kwargs)
            )
            monkeypatch.setenv("DASHSCOPE_API_KEY", "private-fixture-key")
            monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://offline.example/v1")
            worker(
                {
                    "kind": kind,
                    "directory": str(directory),
                    "budget": str(budget.path),
                    "phase": "basic",
                    "association": 1,
                    "messages": (
                        [
                            {"role": "system", "content": "fixture"},
                            {
                                "role": "user",
                                "content": json.dumps(
                                    {"messages": [{"role": "user", "content": "fixture"}]}
                                ),
                            },
                        ]
                        if kind == "diagnostic"
                        else [{"role": "user", "content": "fixture"}]
                    ),
                }
            )
    assert len(requests) == budget.read()["requests"] == 1
    output = json.loads((directory / "output.json").read_text())
    if kind == "diagnostic":
        assert json.loads(output["text"])["diagnostics"] == []
        assert (
            json.loads((directory / "raw_output.json").read_text())["text"]
            == "real SDK mock transport output"
        )
    else:
        assert output["text"] == "real SDK mock transport output"
    assert "private-fixture-key" not in budget.path.with_suffix(".jsonl").read_text()


def test_official_task_worker_shared_agent_simulator_accounting(tmp_path, monkeypatch):
    from agent_evolve.live_runtime import ROLE

    budget = Budget.create(tmp_path / "budget.json")
    directory = tmp_path / "evaluation"
    directory.mkdir()
    with deny_network():
        from litellm import ModelResponse
        from tau2.user.user_simulator_base import STOP
        from tau2.utils import llm_utils

        counts = {"agent": 0, "simulator": 0}

        def fake(**kwargs):
            role = ROLE.get()
            counts[role] += 1
            message = {"role": "assistant", "content": "Inspection complete."}
            finish = "stop"
            if role == "simulator":
                message["content"] = "Inspect my order." if counts[role] == 1 else STOP
            elif counts[role] == 1:
                message.update(
                    content=None,
                    tool_calls=[
                        {
                            "id": "probe",
                            "type": "function",
                            "function": {
                                "name": "get_order_details",
                                "arguments": '{"order_id":"#W2378156"}',
                            },
                        }
                    ],
                )
                finish = "tool_calls"
            return ModelResponse(
                model=MODEL,
                choices=[{"index": 0, "finish_reason": finish, "message": message}],
                usage={"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
            )

        monkeypatch.setattr(llm_utils, "completion", fake)
        monkeypatch.setenv("DASHSCOPE_API_KEY", "private-fixture-key")
        monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://offline.example/v1")
        worker(
            {
                "kind": "task",
                "directory": str(directory),
                "budget": str(budget.path),
                "phase": "basic",
                "association": "synthetic",
                "task_id": "1",
                "candidate": "seed",
            }
        )
    result = json.loads((directory / "task/1.json").read_text())
    assert result["official_raw_reward"] == 0.0
    assert budget.read()["requests"] == sum(counts.values()) == 4
    assert counts == {"agent": 2, "simulator": 2}
    assert not budget.read()["stopped"]


def test_semantic_review_can_reject_grounded_but_unsupported_inference(tmp_path, monkeypatch):
    """Synthetic two-response diagnostic; no claim about hosted model quality."""
    from agent_evolve.live_runtime import ROLE

    budget = Budget.create(tmp_path / "budget.json")
    directory = tmp_path / "semantic"
    directory.mkdir()
    finding = {
        "category": "communication_confirmation",
        "finding": "risk",
        "observation": "A synthetic proposed inference.",
        "hypothesis": "Unproven cause.",
        "certainty": "plausible",
        "responsibility": "Unknown",
        "impact": "Unproven.",
        "suggestion": "Check evidence before attributing a cause.",
        "evidence": [
            {"pointer": "/messages/0/content", "quote": "Please help."},
            {"pointer": "/messages/1/content", "quote": "I will help."},
        ],
    }
    payload = {
        "messages": [
            {"role": "user", "content": "Please help."},
            {"role": "assistant", "content": "I will help."},
        ]
    }
    seen = []
    with deny_network():
        from litellm import ModelResponse
        from tau2.utils import llm_utils

        def fake(**kwargs):
            seen.append(kwargs)
            assert ROLE.get() == "diagnostic" and kwargs["timeout"] == 90
            if len(seen) == 2:
                view = json.loads(kwargs["messages"][1]["content"])
                assert view["messages"][0]["trace_pointer"] == "/messages/0"
                assert view["proposed_findings"][0]["observation"] == finding["observation"]
            return ModelResponse(
                model=MODEL,
                choices=[
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(
                                {"diagnostics": [finding] if len(seen) == 1 else []}
                            ),
                        },
                    }
                ],
                usage={"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
            )

        monkeypatch.setattr(llm_utils, "completion", fake)
        monkeypatch.setenv("DASHSCOPE_API_KEY", "private-fixture-key")
        monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://offline.example/v1")
        worker(
            {
                "kind": "diagnostic",
                "directory": str(directory),
                "budget": str(budget.path),
                "phase": "structured",
                "association": "fixture",
                "request_seconds": 90,
                "messages": [
                    {"role": "system", "content": "fixture"},
                    {"role": "user", "content": json.dumps(payload)},
                ],
            }
        )
    assert len(seen) == budget.read()["requests"] == 2
    assert (
        json.loads(json.loads((directory / "output.json").read_text())["text"])["diagnostics"] == []
    )
    assert (directory / "raw_output.json").exists() and (directory / "review_raw.json").exists()


def test_provider_failure_preserves_partial_trace_without_official_zero(tmp_path, monkeypatch):
    from agent_evolve.baseline import ProviderError

    budget = Budget.create(tmp_path / "budget.json")
    directory = tmp_path / "partial"
    directory.mkdir()

    with deny_network():
        from tau2.utils import llm_utils

        def fail(**kwargs):
            raise RuntimeError("Synthetic provider outage")

        monkeypatch.setattr(llm_utils, "completion", fail)
        monkeypatch.setenv("DASHSCOPE_API_KEY", "private-fixture-key")
        monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://offline.example/v1")
        with pytest.raises(ProviderError):
            worker(
                {
                    "kind": "task",
                    "directory": str(directory),
                    "budget": str(budget.path),
                    "phase": "basic",
                    "association": "fixture",
                    "task_id": "1",
                    "candidate": "seed",
                    "limits": {"steps": 64},
                }
            )
    trace = json.loads((directory / "task/partial_trace.json").read_text())
    result = json.loads((directory / "task/1.json").read_text())
    assert result["status"] == "infrastructure_error" and budget.read()["stopped"]
    assert trace["messages"] and result["messages"] == trace["messages"]
    assert result["official_task_reward"] is None and not (directory / "task/1.raw.json").exists()
