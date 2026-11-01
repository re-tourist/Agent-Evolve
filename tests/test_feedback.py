"""Synthetic diagnostic counterexamples, not observed model failure statistics."""

import copy
import json
from pathlib import Path

import pytest

from agent_evolve.feedback import diagnose


def result(messages=(), reward=0.0, reason="user_stop", excluded=False):
    return {
        "messages": list(messages),
        "official_task_reward": reward,
        "termination_reason": reason,
        "excluded_from_task_metrics": excluded,
    }


def call(arguments=None, role="assistant"):
    return {
        "role": role,
        "tool_calls": [
            {"id": "call-1", "name": "inspect", "arguments": {} if arguments is None else arguments}
        ],
    }


def tool(content="Error: server unavailable", error=True, **fields):
    return {
        "role": "tool",
        "id": "call-1",
        "requestor": "assistant",
        "error": error,
        "content": content,
        "execution_status": "executed",
        **fields,
    }


def of_type(feedback, name):
    return [d for d in feedback["diagnostics"] if d["type"] == name]


def resolve(document, pointer):
    for part in pointer.split("/")[1:]:
        document = document[int(part)] if isinstance(document, list) else document[part]
    return document


def test_explicit_tool_error_with_resolvable_evidence_and_no_mutation():
    trace = result([call(), tool()])
    before = copy.deepcopy(trace)
    feedback = diagnose(trace)
    (error,) = of_type(feedback, "tool_execution_error")
    assert error["certain"] is True
    assert resolve(trace, error["evidence"][0]["pointer"]) is True
    assert error["evidence"][-1]["pointer"] == "/messages/0/tool_calls/0"
    assert of_type(feedback, "uncertain_failure")[0]["certain"] is False
    assert not of_type(feedback, "invalid_tool_arguments")
    assert trace == before
    assert json.loads(json.dumps(feedback)) == feedback


@pytest.mark.parametrize(
    "content",
    [
        "Error: free-text claim",
        '{"error":"business data"}',
        "inspect() missing 1 required positional argument: 'id'",
    ],
)
def test_normal_tool_responses_are_not_errors_even_if_content_mentions_error(content):
    feedback = diagnose(result([call(), tool(content=content, error=False)], reward=1))
    assert not of_type(feedback, "tool_execution_error")
    assert not of_type(feedback, "invalid_tool_arguments")
    assert not of_type(feedback, "uncertain_failure")


@pytest.mark.parametrize(
    "text",
    [
        "Error: RetailTools.inspect() missing 1 required positional argument: 'id'",
        "Error: inspect() got an unexpected keyword argument 'wrong'",
    ],
)
@pytest.mark.parametrize("quoted", [False, True])
def test_argument_binding_markers_require_error_and_matching_preceding_call(text, quoted):
    trace = result([call(), tool(content=json.dumps(text) if quoted else text)])
    (diagnostic,) = of_type(diagnose(trace), "invalid_tool_arguments")
    assert diagnostic["certain"] is True
    assert diagnostic["evidence"][0]["pointer"] == "/messages/1/content"


@pytest.mark.parametrize("arguments", [[], "not parsed", 3])
def test_non_object_normalized_arguments_are_observable_anomaly(arguments):
    trace = result([call(arguments)])
    (item,) = of_type(diagnose(trace), "invalid_tool_arguments")
    assert item["evidence"][0]["pointer"] == "/messages/0/tool_calls/0/arguments"


def test_rejected_call_is_not_reported_as_executed_or_argument_error():
    trace = result([call(), tool(execution_status="rejected")])
    (item,) = of_type(diagnose(trace), "tool_execution_error")
    assert "before execution" in item["explanation"]
    assert not of_type(diagnose(trace), "invalid_tool_arguments")


@pytest.mark.parametrize("prefix", [[], [call(), call()], [call(role="user")]])
def test_absent_duplicate_or_wrong_actor_call_cannot_establish_argument_binding(prefix):
    trace = result([*prefix, tool("Error: inspect() missing 1 required positional argument: 'id'")])
    feedback = diagnose(trace)
    assert of_type(feedback, "tool_execution_error")
    assert not of_type(feedback, "invalid_tool_arguments")


@pytest.mark.parametrize("reason", ["max_steps", "too_many_errors", "user_error", "timeout"])
def test_abnormal_termination_observation_is_not_agent_failure(reason):
    feedback = diagnose(result(reason=reason, reward=None, excluded=True))
    (item,) = of_type(feedback, "task_completion")
    assert item["certain"] is True and "abnormally" in item["explanation"]
    assert not of_type(feedback, "uncertain_failure")


@pytest.mark.parametrize("reward", [None, True, float("nan"), -1, 2])
def test_unavailable_invalid_or_excluded_rewards_do_not_become_business_failure(reward):
    assert not of_type(diagnose(result(reward=reward)), "uncertain_failure")
    assert not of_type(diagnose(result(excluded=True)), "uncertain_failure")


def test_hidden_details_free_text_and_unknown_termination_cannot_leak():
    trace = result([call(), tool("SECRET_ANSWER", error=False)], reason="SECRET_REASON")
    trace.update(
        evaluation_details={"action_checks": ["SECRET_REFERENCE_SEQUENCE"]},
        task={"target": "SECRET_TARGET"},
        raw_data="SECRET_RAW",
    )
    trace["messages"][0]["content"] = "SECRET_DIALOGUE"
    assert "SECRET" not in json.dumps(diagnose(trace))
    assert of_type(diagnose({}), "task_completion")[0]["certain"] is False


def test_alternative_valid_paths_and_order_do_not_invent_reference_requirements():
    for messages in [
        [],
        [call()],
        [call(), tool(error=False)],
        [call(), tool(error=False), call(), tool(error=False)],
    ]:
        diagnostics = diagnose(result(messages))
        assert {d["type"] for d in diagnostics["diagnostics"]} == {
            "task_completion",
            "uncertain_failure",
        }
        completion = of_type(diagnostics, "task_completion")[0]
        assert "early termination" in completion["explanation"]


def test_frozen_actual_framework_projection_matches_expected_feedback():
    root = Path(__file__).parent / "fixtures/m4"
    trace = json.loads((root / "scripted_retail_task0.json").read_text())
    example = json.loads((root / "feedback_example.json").read_text())
    feedback = diagnose(trace)
    assert example["feedback"] == feedback
    assert {d["type"] for d in feedback["diagnostics"]} == {"task_completion", "uncertain_failure"}
    for item in feedback["diagnostics"]:
        for evidence in item["evidence"]:
            resolve(trace, evidence["pointer"])


def test_recovered_tool_error_does_not_imply_task_failure():
    trace = result([call(), tool(), call(), tool(error=False)], reward=1.0)
    feedback = diagnose(trace)
    assert of_type(feedback, "tool_execution_error")
    assert not of_type(feedback, "uncertain_failure")


def test_existing_m2_synthetic_fixture_has_no_official_reward_or_tool_error():
    from agent_evolve.baseline import Config, FixtureBackend, Prompt, normalize

    config = Config(
        mode="mock",
        backend="fixture",
        task_ids=("fixture-retail-001",),
        instruction="fixture instruction",
        output_dir="unused",
        run_id="unused",
    )
    backend = FixtureBackend()
    raw = backend.run(
        backend.tasks(config.task_ids)[0], config, Prompt(config.instruction, backend.policy)
    )
    feedback = diagnose(normalize(raw))
    assert {d["type"] for d in feedback["diagnostics"]} == {"task_completion"}
