# M2-A validation — actual evidence, 2026-11-01

Scope: no-model engineering checks and scripted Mock only. **Paid model/API calls: 0**.
Source baseline afb0e8e plus recorded M2 working tree on codex/m2-baseline-trace;
project source hashes, pinned upstream sources and Retail data hashes are in
M2A_SOURCE_MANIFEST.json. No upstream tracked file, root uv.lock, original v0.2 plan,
or user environment configuration was changed.

Environment: Windows 11 AMD64, CPython 3.12.8, local uv 0.9.5. Root pytest 8.4.2,
ruff 0.14.14. Isolated tau2 2.0.0 / LiteLLM 1.82.6, full transitive versions fixed
in environments/tau/uv.lock. No voice extras, GPU or GEPA installed for M2.

## Repository audit and initial checks
- Clean initial git status, codex/m1-foundation, HEAD afb0e8e; HTTPS origin unchanged.
- All required governance files existed and were read, including original v0.2 plan.
- Initial M1 suite: `uv --cache-dir .cache/uv run --offline --frozen python -m pytest
  --basetemp=.cache/pytest-m2-initial -q` → exit 0, **2 passed in 1.36s**.
- No M1 repair required. Existing unverified remote CI and upstream dependency
  conflict recorded; separate locked τ environment avoids modifying M1 dependencies.

## Unit/fixture and CI-equivalent checks
`uv` below denotes `.bootstrap/Scripts/uv.exe --cache-dir .cache/uv`.

| Actual command after that prefix | Exit | Key result |
|---|---|---|
| `run --offline --frozen python -m pytest tests/test_baseline.py --basetemp=.cache/pytest-m2-narrow -q` | 0 | 38 passed in 2.12s (initial narrow suite) |
| `run --offline --frozen python -m pytest --basetemp=.cache/pytest-m2-final-wiring -q` | 0 | **41 passed, 6 skipped in 2.83s** |
| `run --offline --frozen ruff check .` | 0 | All checks passed |
| `run --offline --frozen ruff format --check .` | 0 | 8 files already formatted |

The 6 skips in the root environment are explicit opt-in upstream tests, not hidden
failures. Those same tests actually ran and passed in the separate environment.
CI keeps dependencies provisioned from registries, then runs no-key lint/format/tests,
package import and fixture CLI. Remote GitHub Actions is **Not run / not pushed**.
`uv run --offline --frozen python -c "import agent_evolve; print(agent_evolve.__version__)"`
also ran in M2-A, exit 0, output 0.1.0. Root smoke verifies installed metadata.
No live job or credentials in CI.

## Final native offline CLI / upstream checks
Actual command, expected/actual exit, runtime and stdout/stderr are retained in
M2A_COMMAND_RESULTS.json. `<repo>` is a path-redaction placeholder, not shell syntax.
These native-permission runs still execute the project's socket/DNS denial guard.

| Command | Exit | Wall seconds |
|---|---|---|
| `"<repo>\.bootstrap\Scripts\uv.exe" --cache-dir .cache/uv run --offline --frozen python -m agent_evolve.baseline --config .cache/m2-mock.json` | 0 | 1.032 |
| `"<repo>\environments\tau\.venv\Scripts\python.exe" -m agent_evolve.baseline --config .cache/m2-tau_preflight.json` | 0 | 11.859 |
| `"<repo>\environments\tau\.venv\Scripts\python.exe" -m agent_evolve.baseline --config .cache/m2-tau_mock-004.json` | 0 | 25.656 |
| `"<repo>\environments\tau\.venv\Scripts\python.exe" -m pytest tests/integration/test_tau.py --basetemp=.cache/pytest-m2-evidence-final -q` | 0 | 33.937 |
| `"<repo>\.bootstrap\Scripts\uv.exe" --cache-dir .cache/uv run --offline --frozen python -m agent_evolve.baseline --config examples/m2/live_proposed.json` | 2 | 0.61 |

The final opt-in suite passed **6 tests** (see exact pytest elapsed time in JSON).
It proves real Retail DB mutation does not reach another/new environment, Agent
histories and Prompt instances are separate, same/different task runs are fresh,
official tools and evaluator work with scripted participants, Judge tasks are refused,
and fake OpenAI SDK / upstream UserError faults are classified without a network call.
A sixth test constructs configured official Agent/UserSimulator objects while both
model generation functions are patched to fail; it never starts a live simulation.
This is official-framework execution, **not real LLM Agent performance**.

## Actual outputs
- `runs/m2/fixture-evidence-002/`: synthetic fixture, official Reward unavailable.
- `runs/m2/tau-preflight-evidence-002/`: actual task 0/Policy load+hash, no simulation.
- `runs/m2/tau-scripted-evidence-004/`: official task 0, deterministic inspection
  script + scripted User, actual tool response, official ALL evaluation **Reward 0**,
  DB check false. Inspection did not solve the task; no success-rate claim.
- Task 1 and repeated task 0 exercised under `.cache/pytest-m2-evidence-final/`.
- Portable inspected excerpt: `M2A_MOCK_EXAMPLE.json`. Full local artifacts stay ignored.
- Proposed Live config: actual exit **2**, LiveNotApprovedError before backend/output.

Missing model usage/cost remains null/unavailable, not a manufactured 0. Upstream
framework aggregate cost 0 with absent per-message costs is kept only in raw; the
normalized result now requires complete per-message estimates before reporting cost.
Actual duration/wall time is recorded independently from unavailable provider latency.

## Failures found and resolved (not suppressed)
- Early ruff reported style/import findings; formatter/fixes applied, no rule disabled.
- First official scripted run had no tool message: the User mistook the built-in
  greeting for a stop condition. Next check also found the Agent counted upstream
  initial history as its own first call. Fixed instance-local scripted turn state;
  assertions requiring real tool calls/responses stayed unchanged and passed.
- Windows sandbox runs printed pytest results but hung at process exit. A timed
  faulthandler dump located LiteLLM async HTTP client cleanup creating an asyncio
  socket pair blocked by the sandbox. These runs were **not reported as successful
  command exits**. Seven identified helpers from this turn's new venv were stopped,
  with exact executable-path rechecks. Native reruns exited 0 with network denial
  inside the test/runner; no upstream patch or forced successful exit was used.
- Upstream emits one audioop deprecation warning under Python 3.12 (import path
  reaches voice utilities despite text mode). Warning remains visible; no suppression.
- Final review found framework default-zero cost aggregation. Added a regression
  test and unavailable-cost normalization, then reran the official scripted evidence.

## Remaining limits and stop gate
Live mode intentionally unavailable in M2-A, even if a user supplies keys or an
approval environment flag. Provider interoperability, real Simulator behavior,
DeepSeek non-thinking request configuration, strict global Token/RMB admission
and actual hosted usage accounting await explicit M2-B approval/review. Proposal:
`../experiments/M2_LIVE_RUN_PROPOSAL.md`. No M2-B or M3 execution performed.
