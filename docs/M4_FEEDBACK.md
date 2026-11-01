# M4-A: trace-grounded feedback, offline only

Current scope is four conservative observations, not a complete failure classifier
or evidence of Prompt improvement. No LLM Judge, API request or formal optimization.

## Interface audit / information boundary
The source of truth is pinned tau da0835f6c67baef58bdda18f2a3b037dfb3a1754:
[ToolMessage](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/data_model/message.py),
[Environment.get_response](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/environment/environment.py).
Local checked source was read; web fetch was unavailable, so no floating-doc claim.

| Input | Meaning / use |
|---|---|
| messages[].role, tool_calls[].id/name/arguments, tool response id/requestor/content/error/execution_status | Actually recorded interaction. A response may execute and report an error, or be rejected before execution. Call/response pairing uses unique preceding ID plus requestor, never a prescribed sequence. |
| termination_reason | Runner observation, not proof of business completion or why a participant stopped |
| official_task_reward | M2-normalized original official Reward; null/excluded failures are not business zeros |
| evaluation_details / reward_info, especially action_checks.action.arguments | May include reference actions, hidden target checks and expected parameters. Never read or copied by diagnostics. |
| Task definitions, DB target, test traces, messages.raw_data | Not diagnostic inputs for optimization; no reference trajectory comparison |

M2 normalize preserves raw details locally for audit. Storage is not authorization
to send those details to reflection. The diagnostic output copies no raw text,
argument values or tool result bodies. It emits fixed explanations, flags, types,
known termination labels and scalar reward only; no hidden evaluator criteria.

The pure function cannot infer train/test provenance from arbitrary input. The
existing TauEvaluator TaskSets guard rejects test/unlisted examples BEFORE worker
execution; GEPA still receives train/validation only and test_set=None. Direct
offline inspection of a trace does not itself authorize sending it to an optimizer.

## Minimal API / certainty
`agent_evolve.feedback.diagnose(normalized_result) -> JSON dict` returns
schema_version plus diagnostics. Each item contains type, certain, explanation and
evidence[] with JSON Pointer locations in the original normalized trace.
Evidence values are either literal flag/reward/termination values or a safe derived
descriptor (observed_type, observed_marker, association); they are not raw excerpts.
Unknown/missing termination uses an unavailable descriptor; empty pointer means root.

| Type | Required evidence and limit |
|---|---|
| tool_execution_error | Tool role + boolean error=true. Rejected execution_status is explicitly described as NOT executed. Error does not establish Agent responsibility or relation to Reward. |
| invalid_tool_arguments | Non-object arguments in normalized trace, OR error=true + unique preceding call/actor + exact Python missing-required/unexpected-keyword binding marker in tool content. JSON-quoted error strings are supported. Marker reports do not prove task-level causality. |
| task_completion | Known termination reason: observed participant stop or explicit abnormal termination (max_steps, too_many_errors, timeout, etc.). user_stop/agent_stop alone is never labeled early or successful. Unknown reason remains uncertain. |
| uncertain_failure | Valid admitted official Reward below 1. Root cause remains uncertain even alongside local errors, since errors can be recovered and Reward is not causal evidence. Excluded/missing/invalid rewards never become zeros. |

`certain=true` means the listed observation/marker was recorded, NOT that its
root cause, responsibility, early intent or task impact is proven. No match means
no specific diagnosis, not evidence of correctness. Business-invalid values, errors
inside successful JSON results, malformed provider JSON rejected before a trace is
recorded, missing trace events and paraphrased errors are not classified by guesswork.
No tool schema engine or multilingual free-text classifier is introduced.

## GEPA connection: optional, same score
The pinned GEPA 8c7b697a71977980afc7537dac0881e784eef99f accepts evaluator return
`(score, info_dict)`. M3's basic feedback remains the default:

```python
TauEvaluator(..., feedback_mode="basic")       # unchanged basic info
TauEvaluator(..., feedback_mode="structured")  # adds info["structured_feedback"]
```

OptimizationConfig also accepts `feedback_mode` with these same two values and
persists it in config.json. No model, optimizer or official score is changed.
Identity/Policy/RewardInfo/admission checks still run first. Infrastructure faults
abort as before; structured feedback is not a way to admit an invalid score.
Actual added diagnostics are retained in existing evaluation.json / evaluations.jsonl
and passed as GEPA info, not combined into weighted reward. Existing Live rejection
and Qwen single-task configuration are unchanged. No new execution command is needed.

## Inspectable existing-trace example
[Observable fixture](../tests/fixtures/m4/scripted_retail_task0.json) and
[feedback with provenance](../tests/fixtures/m4/feedback_example.json) project
the existing M3 gepa-offline-002 task-0 trace, preserving message/call indices and
actual observed fields. They remove text/bodies and hidden Reward details.
Original file path and SHA-256 are recorded; source full trace remains ignored locally.

Actual observation: get_order_details response at /messages/3 has error=false,
execution_status=executed. End reason user_stop, official Reward 0. Output:
- task_completion: certain observation of user_stop, no early-stop inference.
- uncertain_failure: cause unknown, official_task_reward=0. No tool error or
  missing-reference-step diagnosis. Different valid tool paths remain possible.

To inspect without importing tau/GEPA or accessing a network:
```powershell
uv run --offline --frozen python -c "import json; from pathlib import Path; from agent_evolve.feedback import diagnose; print(json.dumps(diagnose(json.loads(Path('tests/fixtures/m4/scripted_retail_task0.json').read_text())), indent=2))"
```
For narrow and full verification, see [actual validation](validation/M4A_VALIDATION.md).
Synthetic bad arguments/provider cases are engineering fixtures, not LLM failure
counts. A next step would be separately approved observation on real Agent traces;
no M4-B, M5, API run or comparison is performed here.
