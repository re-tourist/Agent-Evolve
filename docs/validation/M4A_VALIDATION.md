# M4-A actual offline acceptance — 2026-11-01

Initial Git tree clean at 7236b65; work on codex/m4a-structured-feedback. No real
API/model calls, formal GEPA search/comparison, M4-B or M5. Python 3.12.8 / uv 0.9.5.
The current user explicitly authorized M4-A despite older scope notes saying no M4.
No Qwen API configuration, entry, tests or pending approval requirement changed.

## Actual commands and results
`uv` below is the repository-local `.bootstrap/Scripts/uv.exe`. In PowerShell set
annotated environment variables with `$env:NAME='1'` before the command.

| Command | Exit | Actual output |
|---|---|---|
| `uv --cache-dir .cache/uv run --offline --frozen python -m pytest tests/test_feedback.py tests/test_gepa_adapter.py -q --basetemp=.cache/pytest-m4-narrow-final` | 0 | 66 passed, 1.83s |
| `uv --cache-dir .cache/uv run --offline --frozen python -m pytest -q --basetemp=.cache/pytest-m4-root-final` | 0 | 111 passed / 18 opt-in skipped, 7.40s |
| `AGENT_EVOLVE_TAU_TESTS=1 environments/tau/.venv/Scripts/python.exe -m pytest tests/integration/test_feedback_tau.py tests/integration/test_tau.py tests/integration/test_gepa_tau.py tests/integration/test_qwen_transport.py -q --tb=short --basetemp=.cache/pytest-m4-tau` | 0 | 11 passed / 2 warnings, 35.22s |
| `AGENT_EVOLVE_GEPA_TESTS=1 AGENT_EVOLVE_TAU_WORKER_TESTS=1 environments/gepa/.venv/Scripts/python.exe -m pytest tests/integration/test_gepa.py -q --tb=short --basetemp=.cache/pytest-m4-gepa-full` | 0 | 7 passed, 30.75s |
| `AGENT_EVOLVE_GEPA_TESTS=1 uv --cache-dir .cache/uv run --project environments/gepa --offline --frozen python -m pytest tests/integration/test_gepa.py -q --basetemp=.cache/pytest-m4-gepa` | 0 | 6 passed / 1 intentional tau-worker skip, 3.95s |
| `uv --cache-dir .cache/uv run --offline --frozen ruff check .` | 0 | All checks passed |
| `uv --cache-dir .cache/uv run --offline --frozen ruff format --check .` | 0 | 19 files already formatted |
| `git diff --check` | 0 | No whitespace errors |

All root opt-in skips were separately executed as 11+7 tests above. Native Windows
permissions were used for upstream tests with socket/DNS denial and local Mock HTTP,
not permission for a model request. Upstream audioop and LiteLLM event-loop
deprecation warnings remain visible. No remote CI / Linux run claimed (not pushed).
Initial style check found long explanation strings; split string literals without
changing meaning. No test failures or suppressed checks in final results.

## Evidence classes and conclusions
- Pure/synthetic tests: explicit error flag; ordinary responses containing "error"
  not flagged; argument-binding markers; non-object normalized arguments; rejected
  versus executed calls; absent/duplicate/wrong-actor association abstention; normal
  stops, explicit step/time/error termination; unavailable/invalid/excluded Reward;
  recovered errors with Reward 1; no reference-path rule; serialization/evidence
  pointers; hidden target/reference/raw dialogue sentinel never copied. Existing
  M2 FixtureBackend has no official Reward and receives no invented business failure.
- Actual official Retail tool: get_order_details({}) produces error=true and an
  argument-binding diagnostic; known order lookup produces a normal response and
  no error diagnostic. Inputs are synthetic probes, not a real LLM failure sample.
- Actual M3 scripted trace: existing gepa-offline-002 task 0 remains immutable.
  Source SHA 8a8ea3a06f5fe58a1bd5130500a1173736f3403f9fdcf3404d7f59df465bfd58.
  Only observable structural fields are frozen in tests/fixtures/m4; indices and
  values are retained, hidden evaluation_details and message bodies are absent.
  No new evaluation was needed to produce the example. Full-source and projected
  diagnostics match: user_stop observation plus uncertain_failure on official 0;
  zero tool/argument error findings. No abnormal early-stop inference.
- Real GEPA engine, local deterministic reflection/synthetic worker: both basic
  and structured paths serialize and preserve existing score and candidate behavior.
  Adapter test compares identical official-style fixture scores, verifies extra
  feedback only and rejects reserved test examples. This is an offline contract
  test, not an optimization experiment or Agent performance comparison.
- Real APIs / real Agent diagnostic precision / feedback benefit: NOT RUN / UNKNOWN.
  The standalone function does not identify splits; TaskSets guards optimizer access.

`M4_FEEDBACK.md` includes the exact no-network example-inspection command; it was
executed with exit 0 and returned the same two findings as feedback_example.json.
No hidden action checks, gold state, task target or free-text values appear in output.
Static review also confirmed original/full and projected diagnostic equality,
six source/fixture SHA-256 matches and 26 valid local Markdown links. The temporary
review helper needed explicit UTF-8 on Windows; that helper is ignored, not product code.

## Tested source identity (working tree based on 7236b65)
SHA-256 before local commit:
- src/agent_evolve/feedback.py: e9be63ae5114a2422f1a602dc4dea4fb93ee64dbb07ea3271f737d61dcb91865
- src/agent_evolve/gepa_adapter.py: 20ccbea993af4fce0ced564e1ad1c6b10ba307659130395215a0a171a663b6a6
- src/agent_evolve/optimization.py: 99b42fae713e68f1e90e0745856bae4738c883da7ae6e762257ac6f58164119a
- tests/test_feedback.py: 704694480a250f02d43c103988265500f38972941de318cbb308bb1520be0bee
- scripted_retail_task0.json: 65f7683726d4017dbde4aa25277a2d9be436526b3f8635ee6d00b0b0c51b4d3a
- feedback_example.json: 9446477c727d023064e9c79f97a5d2ff015b93639458e2119c546a82ec9aac56

Original baseline.py, tau_backend.py, qwen_smoke.py, Qwen tests/model setup,
all dependency locks and PROJECT_PLAN v0.2 remain unchanged. Both official tracked
source trees remain clean at the existing pins; no official scoring/task/Policy edit.
Local Git only; no push, Issue mutation, default-branch edit, merge or Release.
Stop at M4-A; the next candidate action is separately approved real trace validation.
