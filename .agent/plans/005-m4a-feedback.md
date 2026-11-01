# M4-A minimal trace diagnostics (offline only)

Initial clean tree: 7236b65, codex/m3b-qwen-preparation; work on
codex/m4a-structured-feedback. Read governance, v0.2 scope/protocol, M2 exports,
M3 evaluator/config/tests and pinned tau ToolMessage/environment/tool code.
No API call is approved; qwen_smoke.py and its model configuration stay unchanged.

Audit: normalized messages expose roles, tool arguments/results, error flag,
requestor/execution_status, termination_reason and official scalar Reward. Raw
evaluation_details/action_checks contain hidden reference actions/arguments; exclude
them, task targets and test examples from feedback. GEPA accepts (score, JSON info).
No reference-path comparison, Judge, provider addition or scoring change.

- [x] Pure diagnostic function: evidence pointers, observation certainty, four types.
- [x] Optional structured feedback in evaluator/config; basic default and score unchanged.
- [x] Frozen observable projection of existing M3 scripted trace and example output.
- [x] Narrow tests, real tau error/normal traces and existing offline regressions.
- [x] Document actual evidence/limits and review diff; local commit at closure, stop at M4-A.

Pins remain tau da0835f6c67baef58bdda18f2a3b037dfb3a1754 and GEPA
8c7b697a71977980afc7537dac0881e784eef99f. No new dependency. Recognition is
conservative: explicit tool errors, normalized argument shape / exact Python
binding-error markers, termination observations, uncertain cause for failed Reward.
No generic schema validator or text classifier. Full failure causality unverified.

Outcome: narrow 66 passed; root 111 passed / 18 opt-in skips, all opt-in cases
executed separately (official tau 11 passed; full GEPA 7 passed). Ruff check/format
passed. Initial style issues corrected, no test failure hidden. Existing task-0
scripted trace yields only user_stop and uncertain_failure, no invented tool error.
Validation/source hashes: docs/validation/M4A_VALIDATION.md. No model/API call,
formal optimization or M4-B/M5. Qwen preparation preserved. Await separate approval.
