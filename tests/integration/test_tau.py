"""Opt-in real upstream environment/evaluator tests; participants are scripted, not LLMs."""

import json
import os
from dataclasses import replace
from pathlib import Path

import pytest

from agent_evolve.baseline import Config, Prompt, deny_network, execute

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_TESTS") != "1",
    reason="Run explicitly in the pinned environments/tau environment",
)
CHECKOUT = Path(__file__).resolve().parents[2] / ".cache/tau2-source"


@pytest.fixture
def backend():
    with deny_network():
        from agent_evolve.tau_backend import TauBackend

        yield TauBackend(str(CHECKOUT))


def test_real_retail_database_and_history_isolation(backend):
    from tau2.data_model.message import UserMessage
    from tau2.runner import build_environment

    from agent_evolve.tau_backend import make_agent

    with deny_network():
        first = build_environment("retail")
        second = build_environment("retail")
        order_id = next(iter(first.tools.db.orders))
        original = second.tools.db.orders[order_id].status
        first.tools.db.orders[order_id].status = "ISOLATION_TEST_MUTATION"
        assert second.tools.db.orders[order_id].status == original
        assert build_environment("retail").tools.db.orders[order_id].status == original
        prompt = Prompt("A", backend.policy)
        agent = make_agent(prompt, first.get_tools(), "mock/a", {}, scripted=True)
        a, b = agent.get_init_state(), agent.get_init_state()
        a.messages.append(UserMessage(role="user", content="Only history A"))
        assert b.messages == []
        assert a.system_messages[0].content == prompt.system
        other = make_agent(
            Prompt("B", backend.policy), second.get_tools(), "mock/b", {}, scripted=False
        )
        assert other.get_init_state().system_messages[0].content != prompt.system
        assert other.domain_policy == agent.domain_policy == backend.policy


def test_real_official_runner_reward_repeat_and_different_tasks(backend, tmp_path):
    config = Config(
        mode="mock",
        backend="tau",
        task_ids=("0", "1"),
        num_tasks=2,
        instruction="Test instruction",
        output_dir=str(tmp_path),
        run_id="first",
        tau_checkout=str(CHECKOUT),
        agent_model="mock/scripted",
        user_model="mock/user",
    )
    first = execute(config, backend=backend)
    repeat = execute(
        replace(config, task_ids=("0",), num_tasks=1, run_id="repeat"), backend=backend
    )
    for directory, task_id in [(first, "0"), (first, "1"), (repeat, "0")]:
        result = json.loads((directory / f"{task_id}.json").read_text())
        assert result["status"] == "task_failure"  # inspection script does not solve the task
        assert result["official_task_reward"] == 0.0
        assert result["evaluation_details"]["db_check"]["db_match"] is False
        assert any(m.get("tool_calls") for m in result["messages"])
        assert any(m.get("role") == "tool" for m in result["messages"])
        assert result["reward_source"] == "official_evaluator_on_scripted_trace"
        assert result["provider_cost"] == {"agent": None, "user": None}
    a = json.loads((first / "0.raw.json").read_text())
    b = json.loads((repeat / "0.raw.json").read_text())
    assert [m.get("content") for m in a["messages"]] == [m.get("content") for m in b["messages"]]


def test_official_preflight_and_judge_task_refusal(backend, tmp_path):
    config = Config(
        mode="offline",
        backend="tau",
        task_ids=("2",),
        instruction="Test",
        output_dir=str(tmp_path),
        run_id="preflight",
        tau_checkout=str(CHECKOUT),
    )
    out = execute(config, backend=backend)
    assert json.loads((out / "2.json").read_text())["status"] == "preflight_only"
    out = execute(replace(config, mode="mock", run_id="judge-refused"), backend=backend)
    result = json.loads((out / "2.json").read_text())
    assert result["official_task_reward"] is None
    assert result["status"] == "runner_error"


@pytest.mark.parametrize("source", ["provider", "simulator"])
def test_official_adapter_fault_types(backend, tmp_path, monkeypatch, source):
    import httpx
    from openai import APIConnectionError
    from tau2.user.user_simulator_base import UserError

    def failed(*args, **kwargs):
        if source == "provider":
            raise APIConnectionError(request=httpx.Request("POST", "https://invalid.example"))
        raise UserError("Synthetic simulator exception")

    monkeypatch.setattr("tau2.runner.run_simulation", failed)
    config = Config(
        mode="mock",
        backend="tau",
        task_ids=("0",),
        instruction="Test",
        output_dir=str(tmp_path),
        run_id=source,
        tau_checkout=str(CHECKOUT),
    )
    directory = execute(config, backend=backend)
    result = json.loads((directory / "0.json").read_text())
    assert result["status"] == (
        "infrastructure_error" if source == "provider" else "simulator_error"
    )
    assert result["official_task_reward"] is None
    assert result["excluded_from_task_metrics"] is True


def test_official_model_configuration_construction_without_generation(
    backend, tmp_path, monkeypatch
):
    from agent_evolve.tau_backend import build_live_components

    def forbidden(*args, **kwargs):
        raise AssertionError("Construction must never request a model")

    monkeypatch.setattr("tau2.agent.llm_agent.generate", forbidden)
    monkeypatch.setattr("tau2.user.user_simulator.generate", forbidden)
    config = Config(
        mode="live",
        backend="tau",
        task_ids=("0",),
        instruction="Candidate",
        output_dir=str(tmp_path),
        run_id="construction-only",
        agent_model="openai/deepseek-flash",
        user_model="openai/deepseek-flash",
        agent_args={"max_tokens": 512},
        user_args={"max_tokens": 256},
    )
    components = build_live_components(
        config, backend.tasks(("0",))[0], Prompt(config.instruction, backend.policy)
    )
    assert components.agent.llm == components.user.llm == "openai/deepseek-flash"
    assert components.agent.llm_args["max_tokens"] == 512
    assert components.user.llm_args["max_tokens"] == 256
    assert components.agent.system_prompt == Prompt(config.instruction, backend.policy).system
    assert components.environment.get_policy() == backend.policy
    # Deliberately no components.run() or participant generation.
