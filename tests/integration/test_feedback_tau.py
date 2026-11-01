"""Actual official Retail errors; synthetic tool inputs, no model calls."""

import os

import pytest

from agent_evolve.baseline import deny_network
from agent_evolve.feedback import diagnose

pytestmark = pytest.mark.skipif(
    os.environ.get("AGENT_EVOLVE_TAU_TESTS") != "1",
    reason="Requires pinned tau environment; no API",
)


def test_official_tool_error_argument_binding_and_normal_response():
    with deny_network():
        from tau2.data_model.message import ToolCall
        from tau2.runner import build_environment

        environment = build_environment("retail")
        for arguments, expected in [({}, True), ({"order_id": "#W2378156"}, False)]:
            call = ToolCall(id="probe", name="get_order_details", arguments=arguments)
            response = environment.get_response(call)
            trace = {
                "messages": [
                    {"role": "assistant", "tool_calls": [call.model_dump()]},
                    response.model_dump(),
                ],
                "termination_reason": "user_stop",
            }
            types = {d["type"] for d in diagnose(trace)["diagnostics"]}
            assert ("tool_execution_error" in types) == expected
            assert ("invalid_tool_arguments" in types) == expected
