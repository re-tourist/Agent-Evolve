"""Pinned official English binding/replay; scripted messages, zero model requests."""

import json
import os
from dataclasses import replace

import pytest

from agent_evolve.baseline import Config, Prompt, deny_network

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_TESTS") != "1", reason="Requires pinned tau environment"
)


def test_reviewed_persona_prompt_isolation_and_official_replay():
    with deny_network():
        from tau2.data_model.message import UserMessage
        from tau2.runner import run_simulation

        from agent_evolve.tau_backend import TauBackend, build_live_components

        backend = TauBackend(".cache/tau2-source")
        legacy = backend.tasks(("13",))[0]
        task = backend.tasks(("13",), protocol="reviewed-en-text")[0]
        assert task["evaluation_criteria"] == legacy["evaluation_criteria"]
        assert task["user_scenario"] != legacy["user_scenario"]
        config = Config(
            mode="live",
            backend="tau",
            task_ids=("13",),
            instruction="Candidate A",
            output_dir="unused",
            run_id="offline-reviewed",
            tau_protocol="reviewed-en-text",
        )
        prompt = Prompt(config.instruction, backend.policy)
        first = build_live_components(config, task, prompt)
        second = build_live_components(
            replace(config, instruction="Candidate B"), task, Prompt("Candidate B", backend.policy)
        )
        context = first.call_context.language
        assert context.persona_id and context.language == "en" and context.mode == "text"
        assert first.user.persona_config == context.persona
        assert first.environment.get_policy() == second.environment.get_policy() == backend.policy
        assert [t.openai_schema for t in first.agent.tools] == [
            t.openai_schema for t in second.agent.tools
        ]
        assert "Candidate A" in first.agent.system_prompt
        assert "Candidate B" not in first.agent.system_prompt
        assert context.agent_language_clause in first.agent.domain_policy
        assert first.agent.get_init_state().messages == second.agent.get_init_state().messages == []
        assert first.environment is not second.environment
        first.user.generate_next_message = lambda message, state: (
            UserMessage(role="user", content="###STOP###"),
            state,
        )
        result = run_simulation(first)
        assert result.reward_info is not None
        assert result.language_context == context
        assert result.reward_info.reward == 0  # Script performs no required business action.
        assert json.loads(first.call_context.model_dump_json())["language"]["task_sha256"]
        with pytest.raises(ValueError, match="reviewed"):
            backend.tasks(("20",), protocol="reviewed-en-text")
        with pytest.raises(ValueError, match="differs"):
            build_live_components(config, legacy, prompt)
