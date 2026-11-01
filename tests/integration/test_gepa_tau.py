"""Candidate injection using actual M2/tau components, without generation."""

import os

import pytest

from agent_evolve.baseline import Prompt, canonical, deny_network, digest

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_TESTS") != "1",
    reason="Requires pinned tau environment; offline only",
)


def test_candidates_preserve_real_policy_tools_and_fresh_state():
    with deny_network():
        from tau2.data_model.message import UserMessage
        from tau2.runner import build_environment

        from agent_evolve.tau_backend import make_agent

        first, second = build_environment("retail"), build_environment("retail")
        policy = first.get_policy()
        tools_hash = digest(canonical([t.openai_schema for t in first.get_tools()]))
        a = make_agent(
            Prompt("candidate A", policy), first.get_tools(), "mock/a", {}, scripted=True
        )
        b = make_agent(
            Prompt("candidate B", policy), second.get_tools(), "mock/b", {}, scripted=True
        )
        state_a, state_b = a.get_init_state(), b.get_init_state()
        assert state_a.system_messages[0].content != state_b.system_messages[0].content
        assert a.domain_policy == b.domain_policy == second.get_policy() == policy
        assert digest(canonical([t.openai_schema for t in second.get_tools()])) == tools_hash
        state_a.messages.append(UserMessage(role="user", content="private history A"))
        assert state_b.messages == []
        order_id = next(iter(first.tools.db.orders))
        old = second.tools.db.orders[order_id].status
        first.tools.db.orders[order_id].status = "candidate A mutation"
        assert second.tools.db.orders[order_id].status == old
        assert build_environment("retail").tools.db.orders[order_id].status == old
