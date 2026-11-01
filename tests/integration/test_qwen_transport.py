"""Pinned tau and LiteLLM with HTTP replaced locally; never a provider request."""

import json
import os

import pytest

from agent_evolve.baseline import deny_network
from agent_evolve.qwen_smoke import BASE, MODEL, Calls, run

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_TESTS") != "1", reason="Pinned tau environment only; no API"
)


def test_litellm_qwen_wire_with_local_transport(tmp_path):
    with deny_network():
        import httpx
        import litellm
        from openai import OpenAI

        requests = []

        def handler(request):
            requests.append(json.loads(request.content))
            assert str(request.url) == BASE + "/chat/completions"
            assert request.headers["authorization"] == "Bearer fake-offline-key"
            return httpx.Response(
                200,
                json={
                    "id": "fake",
                    "object": "chat.completion",
                    "created": 1,
                    "model": MODEL.split("/")[1],
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "c1",
                                        "type": "function",
                                        "function": {"name": "inspect", "arguments": "{}"},
                                    }
                                ],
                            },
                        }
                    ],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
                },
            )

        with httpx.Client(transport=httpx.MockTransport(handler)) as http:
            client = OpenAI(
                api_key="fake-offline-key", base_url=BASE, http_client=http, max_retries=0
            )

            def completion(**kwargs):
                return litellm.completion(client=client, **kwargs)

            calls = Calls(completion, "fake-offline-key", tmp_path)
            response = calls(
                model=MODEL,
                messages=[{"role": "user", "content": "inspect"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "inspect",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ],
                tool_choice="auto",
            )
        assert requests[0]["enable_thinking"] is False
        assert requests[0]["model"] == "qwen-plus-2025-12-01"
        assert requests[0]["max_tokens"] == 512
        assert response.choices[0].message.tool_calls[0].function.name == "inspect"


def test_preflight_offline_needs_no_key(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    assert run("offline-check")["model_calls"] == 0


def test_prepared_entry_with_scripted_provider_only(tmp_path, monkeypatch):
    # Exercise the prepared Live branch under socket denial with a synthetic provider.
    # Artifacts are pytest fixtures, never an actual API experiment.
    with deny_network():
        import tau2.runner
        from litellm import ModelResponse
        from tau2.user.user_simulator_base import STOP
        from tau2.utils import llm_utils

        from agent_evolve import qwen_smoke
        from agent_evolve.baseline import Config

        def local_config(**kwargs):
            kwargs["output_dir"] = str(tmp_path)
            return Config(**kwargs)

        counts = {"agent": 0, "user": 0}
        errors = []
        original_simulation = tau2.runner.run_simulation

        def simulation(*args, **kwargs):
            try:
                return original_simulation(*args, **kwargs)
            except Exception as exc:
                errors.append(str(exc))
                raise

        def fake(**kwargs):
            role = "agent" if kwargs.get("tools") else "user"
            counts[role] += 1
            message = {"role": "assistant", "content": "Scripted inspection complete."}
            finish = "stop"
            if role == "user":
                message["content"] = "Inspect my order." if counts[role] == 1 else STOP
            elif counts[role] == 1:
                finish = "tool_calls"
                message.update(
                    content=None,
                    tool_calls=[
                        {
                            "id": "inspect",
                            "type": "function",
                            "function": {
                                "name": "get_order_details",
                                "arguments": '{"order_id":"#W2378156"}',
                            },
                        }
                    ],
                )
            return ModelResponse(
                model=MODEL,
                choices=[{"index": 0, "finish_reason": finish, "message": message}],
                usage={"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
            )

        monkeypatch.setattr(qwen_smoke, "Config", local_config)
        monkeypatch.setattr(llm_utils, "completion", fake)
        monkeypatch.setattr(tau2.runner, "run_simulation", simulation)
        monkeypatch.setenv("DASHSCOPE_API_KEY", "synthetic-secret")
        result = run("fake-provider-only", live=True, approved=True)
    directory = tmp_path / "fake-provider-only"
    normalized = json.loads((directory / "0.json").read_text())
    assert not errors
    assert result["status"] == "task_failure"
    assert normalized["official_task_reward"] == 0.0
    assert normalized["provider_cost"] == {"agent": None, "user": None}
    assert 1 <= normalized["model_calls"] <= 24
    assert normalized["messages"] and (directory / "0.raw.json").exists()
    assert all("synthetic-secret" not in p.read_text() for p in directory.glob("*.json"))
    with pytest.raises(FileExistsError), deny_network():
        monkeypatch.setenv("DASHSCOPE_API_KEY", "synthetic-secret")
        run("fake-provider-only", live=True, approved=True)
