"""Layer contracts with explicit synthetic evidence, not semantic accuracy evidence."""

import json

from agent_evolve.semantic import validate_interventions


def case():
    view = {
        "policy": "Refund to original payment method.",
        "messages": [
            {"role": "assistant", "content": "Use another payment method."},
            {
                "role": "tool",
                "content": "Error: Payment method should be the original payment method",
            },
        ],
    }
    diagnostic = {
        "category": "policy_violation",
        "observation": {
            "fact": "Tool rejected non-original refund destination.",
            "evidence": [
                {"pointer": "/policy", "quote": "Refund to original payment method."},
                {"pointer": "/messages/1/content", "quote": "Error: Payment method"},
            ],
        },
        "attribution": {
            "responsibility": "Agent",
            "certainty": "observed",
            "hypothesis": None,
            "agent_decision_pointer": "/messages/0",
            "alternatives": "Final reward cause unknown.",
            "reward_causality": "unknown",
        },
        "intervention": {
            "when": "selecting a refund destination",
            "do": "check original method eligibility",
            "because": "the fixed refund Policy requires it",
            "limits": "do not ban a provider if it is the original method",
            "evidence": [{"pointer": "/policy", "quote": "Refund to original payment method."}],
        },
        "impact": "One failed tool call; final outcome causality unknown.",
    }
    return view, diagnostic


def test_fact_attribution_and_conditional_intervention_are_separate():
    view, diagnostic = case()
    result = validate_interventions(json.dumps({"diagnostics": [diagnostic]}), view)
    assert len(result["diagnostics"]) == 1
    assert "Limits:" in result["diagnostics"][0]["suggestion"]
    assert "intervention" not in result["observations"][0]


def test_unknown_cause_preserves_observation_without_speculative_advice():
    view, diagnostic = case()
    diagnostic["attribution"]["responsibility"] = "Unknown"
    result = validate_interventions(json.dumps({"diagnostics": [diagnostic]}), view)
    assert not result["diagnostics"] and result["observations"] and result["rejected"]
    assert "intervention" not in json.dumps(result["observations"])
    diagnostic["intervention"] = None
    result = validate_interventions(json.dumps({"diagnostics": [diagnostic]}), view)
    assert result["observations"] and not result["rejected"]


def test_user_event_cannot_be_an_agent_execution_opportunity():
    view, diagnostic = case()
    view["messages"][0]["role"] = "user"
    result = validate_interventions(json.dumps({"diagnostics": [diagnostic]}), view)
    assert not result["diagnostics"] and result["rejected"]


def test_pointer_only_evidence_resolves_actual_source_without_fabricating_quote():
    view, diagnostic = case()
    diagnostic["observation"]["evidence"] = ["/policy", "/messages/1/content"]
    result = validate_interventions(json.dumps({"diagnostics": [diagnostic]}), view)
    refs = result["diagnostics"][0]["evidence"]
    assert refs[1]["quote"] == view["messages"][1]["content"]
    assert "normalization" in refs[1]
    diagnostic["observation"]["evidence"] = ["/messages/999/content"]
    assert not validate_interventions(json.dumps({"diagnostics": [diagnostic]}), view)[
        "diagnostics"
    ]
