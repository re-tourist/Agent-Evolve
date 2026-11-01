# Qwen single-task preparation validation — 2026-11-01

No real API/model service request. No GEPA Live run, M4 or M5. Clean initial
23509a1; preparation branch codex/m3b-qwen-preparation. Source/runtime acceptance
is offline evidence only, not actual hosted Tool Calling or Agent performance.

## Commands actually run
uv means .bootstrap/Scripts/uv.exe. All final checks exited 0:

| Command (repo root) | Actual result |
|---|---|
| `uv --cache-dir .cache/uv run --offline --frozen python -m pytest -q --basetemp=.cache/pytest-qwen-root-verified` | 80 passed / 16 opt-in skips, 5.03s |
| `uv --cache-dir .cache/uv run --offline --frozen ruff check .` | All checks passed |
| `uv --cache-dir .cache/uv run --offline --frozen ruff format --check .` | 16 files already formatted |
| `environments/tau/.venv/Scripts/python.exe -m agent_evolve.qwen_smoke` | Exit 0; offline_preflight, task 0, trials 1, model_calls 0 |
| `AGENT_EVOLVE_TAU_TESTS=1 environments/tau/.venv/Scripts/python.exe -m pytest tests/integration/test_qwen_transport.py -q --tb=short --basetemp=.cache/pytest-qwen-entry-pass` | 3 passed / 3 warnings, 29.65s |
| `AGENT_EVOLVE_GEPA_TESTS=1 uv --cache-dir .cache/uv run --project environments/gepa --offline --frozen python -m pytest tests/integration/test_gepa.py -q --basetemp=.cache/pytest-qwen-gepa-regression` | 5 passed / 1 deliberate tau-worker skip, 2.59s |

Set the annotated variables with $env:NAME='1' in PowerShell. Native tau tests
used native permissions with explicit socket/DNS denial and local mock HTTP only.
Earlier combined `test_qwen_transport.py test_tau.py test_gepa_tau.py` run at
`.cache/pytest-qwen-native` exited 0, 9 passed / 3 warnings in 35.76s: seven
unchanged official tau/isolation tests plus the initial two Qwen tests. The final
three-case run above adds the complete entry with a scripted Provider. The original
GEPA real tau-subprocess case was not repeated this turn; no new pass claimed.

## What the tests establish
- Local HTTP transport verifies actual LiteLLM/OpenAI SDK URL, bearer header,
  exact Qwen model, tool schema, max_tokens=512, enable_thinking=false and response
  tool-call parsing. No socket goes to Alibaba or any other model service.
- Full prepared entry runs official Retail with synthetic Provider replies,
  one official Reward=0, actual tool trace, null unknown-provider cost, metadata/
  call logs without synthetic Key, and refusal to overwrite a duplicate Run ID.
- Root tests check explicit Live opt-in, shared call/time cap, first-fault stop,
  unrecognized model rejection and secret-free request logs. No currency cap claim.

## Findings fixed / limitations retained
Initial collection collided on duplicate test basenames; renamed integration test.
Default sandbox TEMP could not create pytest numbered directories (18 passed,
15 skipped, 62 setup errors); repository-local --basetemp fixes this without
changing permissions/tests. The new full-entry test exposed missing official
English data in M2 sparse checkout. Added pinned data/tau2/multilingual/en without
editing upstream, and preflight now renders Agent/User prompts. A later duplicate-
run fixture check lost its fake Key at patch.dict teardown; fixed test scope.
Final tests above pass, no failing test suppressed or assertion relaxed.

Three visible upstream warnings remain: LiteLLM missing current event loop,
audioop deprecation, and ProactorEventLoop destructor during network-denied import.
No failed test or real connection resulted. Windows hosted execution, Key/account
model access, cloud compatibility, actual latency/cost and task success remain
unverified. Platform balance/alerts are operator controls, not a strict money cap.

Root/tau/GEPA locks and M2/M3 implementations are unchanged. git diff --check
passes; upstream tracked tree remains clean. SHA-256 of final tested sources:
- qwen_smoke.py: a035cdfec41759d555f4dc31139e712945a6c2afbf62417694e087c400486fa1
- tests/test_qwen_smoke.py: 6e4e0e69ef71093005850132d68dcf7f71ee6fe1b1836c9035aeca2952e7cec1
- tests/integration/test_qwen_transport.py: f9f1b71a33526cf12d7a9ebe0311bf8c64a03c4ab090f46d0cff47dcd42fd56a
- pinned en/pack.yaml: cd14ad9a7aaa298ce54c8c434f2cd1fb55500b13e6fdd1b824d92205a7e4f752

Proposal and operator commands: ../experiments/QWEN_SINGLE_TASK_PROPOSAL.md.
Stop pending explicit approval of the FIRST real Task 0 trial. No automatic next step.
