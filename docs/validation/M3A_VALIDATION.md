# M3-A validation — actual evidence, 2026-11-01

**Real model service/API calls: 0. No M2-B, M3-B, M4 or formal comparison.**
Initial clean branch codex/m2-baseline-trace at eea3bfb; implementation on
codex/m3-gepa-offline. Origin unchanged. Governance/M2 source and validation read.
Initial root regression: 41 passed / 6 explicit opt-in skips in 4.14s.
The integration plan was submitted before implementation in commentary and ExecPlan 003.

## Environment, source identity and dependency boundary
Windows 11 AMD64, Python 3.12.8, uv 0.9.5, pytest 8.4.2, ruff 0.14.14.
GEPA 0.1.4 SHA `8c7b697a71977980afc7537dac0881e784eef99f` core only in its own
environment; LiteLLM not installed there (tested). Original τ environment remains
tau2 2.0.0 / LiteLLM 1.82.6 and SHA `da0835f6c67baef58bdda18f2a3b037dfb3a1754`.
`uv lock --project environments/gepa --default-index https://pypi.org/simple` and
`uv sync --project environments/gepa --frozen --default-index https://pypi.org/simple`
both exited 0: resolved 9 packages, installed 8. No full extra/model SDK installed.
Root and τ locks, M2 implementation/tests, original PROJECT_PLAN.md and both upstream
tracked trees remain unchanged. Source/data/artifact hashes: M3A_SOURCE_MANIFEST.json.
Tested source is eea3bfb plus the dirty working tree; that manifest identifies exact
new code. A later local commit records this tree, not a fabricated prior clean SHA.

## Actual commands/results
`uv` denotes the repository-local .bootstrap/Scripts/uv.exe. Environment assignments
are annotations; in PowerShell set the listed $env variables first. Actual native
upstream runs used native permissions because of M2's diagnosed sandbox exit issue;
the application/worker socket/DNS denial guards remain active.

| Command | Exit | Key result |
|---|---|---|
| `uv --cache-dir .cache/uv run --offline --frozen python -m pytest --basetemp=.cache/pytest-m3-all-final -q` | 0 | 76 passed, 13 skipped in 4.82s |
| `uv --cache-dir .cache/uv run --offline --frozen ruff check .` | 0 | All checks passed! |
| `uv --cache-dir .cache/uv run --offline --frozen ruff format --check .` | 0 | 13 files already formatted |
| `AGENT_EVOLVE_GEPA_TESTS=1 AGENT_EVOLVE_TAU_WORKER_TESTS=1 environments/gepa/.venv/Scripts/python.exe -m pytest tests/integration/test_gepa.py --basetemp=.cache/pytest-m3-contract-final -q` | 0 | 6 passed in 28.38s |
| `AGENT_EVOLVE_TAU_TESTS=1 environments/tau/.venv/Scripts/python.exe -m pytest tests/integration/test_tau.py tests/integration/test_gepa_tau.py --basetemp=.cache/pytest-m3-tau-regression -q` | 0 | 7 passed, 1 warning in 31.49s |
| `AGENT_EVOLVE_GEPA_TESTS=1 uv --cache-dir .cache/uv run --project environments/gepa --offline --frozen python -m pytest tests/integration/test_gepa.py --basetemp=.cache/pytest-m3-ci-equivalent -q` | 0 | 5 passed, 1 skipped in 2.22s |
| `uv run --offline --frozen python -c "import agent_evolve.optimization, agent_evolve.gepa_adapter; print('M3 import OK')"` | 0 | M3 import OK |
| `"<repo>\environments\gepa\.venv\Scripts\python.exe" -m agent_evolve.optimization --config .cache/m3_final_config.json` | 0 | 84.234s; actual stdout in JSON |

Root's 13 skips are the six GEPA tests plus seven τ tests requiring explicit isolated
environments. All 13 were separately executed as the 6+7 rows; no failed test hidden.
The additional CI-equivalent GEPA core run intentionally skips the τ-worker case.
CI configuration now has root offline checks and a GEPA-core deterministic job;
source/package provisioning uses public network, checks make no model request.
**Remote GitHub Actions / Linux execution: Not run (not pushed).**
Final static review: 72 source/artifact SHA-256 entries matched current files;
12 changed/new Markdown files had balanced code fences and 26 valid local links.
git diff --check exited 0. Original project-plan SHA-256 remains
94a7119c5cad094dbae6518f19610e2895d9f24544c0ec67d0087d84893f86ef.

## Distinct evidence classes
1. **Mock unit tests:** injected worker/Provider/timeouts, missing/NaN/bool/mismatched
   RewardInfo, Policy drift, invalid candidates/splits/config, duplicate Run IDs,
   gate rejection and deterministic reflection output. No real scoring claim.
2. **Real GEPA engine + synthetic fixture:** public optimize_anything/config/evaluator,
   Seed→reflection fake→new candidate→train/validation reevaluation→accepted pool
   and parent index. Fixture score 0→1 is deliberately synthetic, not Agent improvement.
   max_evals=1/2 tests consume exactly the cap; engine failure aborts without Best or
   zero task score. Output is serializable and runtime eval_log/metadata retained.
3. **Real GEPA engine + actual scripted Retail:** final CLI described below. Official
   scoring runs, but Agent/User are scripts and Reflection is fake. No hosted model.
4. **Real API experiments:** None / Not run. No genuine performance/cost conclusion.

## Final inspectable optimization run
Run ID **gepa-offline-002**. Exact CLI/84.234s wall/stdout retained in command JSON.
Config points to a fresh run ID; previous run gepa-offline-001 is retained, not overwritten.
Seed 42 reaches both GEPA and M2. Split: train 0, validation 1, reserved test 5;
both development IDs come from official train. No test task is selected/evaluated
or sent to GEPA; test_set=None, and adapter membership checks reject test examples.
The official local loader parses the full task JSON before ID filtering; no claim
of test-file access isolation is made. Target states/criteria stay out of feedback.

Observed chain: seed validation task 1 → seed train task 0 → local reflection fake
proposal → new candidate train task 0 → strict-improvement rejection → Best=seed.
Three actual official evaluations, each Reward **0.0** with six messages and a real
get_order_details tool response. Two distinct candidate texts/hashes are retained;
GEPA's accepted pool contains seed only. Rejected candidate parent linkage is marked
unavailable, never inferred as an optimization-success history. Reflection calls 1;
GEPA budget used 3 / max 4; exact non-budget stop not publicly exposed, reported as
proposal-limit-or-engine-stop rather than invented detail. No improvement claimed.

Local complete artifacts: `runs/m3/gepa-offline-002/`; portable inspected extract:
M3A_OFFLINE_EXAMPLE.json. For every evaluation the original M2 config/Prompt/Policy
hashes/trace/RewardInfo/metadata are retained under evaluations/<sequence>/m2.
GEPA result pool, runtime metadata/eval log, reflection actual input/output, candidate
ledger and Best selection basis are saved separately. Missing usage/provider bill
is unavailable. GEPA fake-callable cost 0 is not an observed provider price/bill.

## State/exception validation and limitations
M2's six original upstream tests passed unchanged. The new candidate isolation test
checks distinct complete System Prompts, identical Policy and tool schema hashes,
separate Agent histories and DB mutation not reaching another/new environment.
Every actual evaluator attempt launches a fresh M2 process, independent run directory
and official environment. No copied database manager or Orchestrator implementation.
Provider/simulator exceptions are injected, not real service failures. A synthetic
timeout retains score=null; failed or unavailable results abort optimization rather
than turning infrastructure failure into task Reward 0. GEPA's internal budget
failure placeholder is not reported as a successful task score.

Early style findings were fixed with ruff/format, no rules/tolerances disabled.
Initial API probe used an upstream auto-generated ignored output directory and a
synthetic evaluator, then project-run-001 and final run-002 used unique directories.
Review added RewardInfo consistency and seed propagation checks; final tests and
run-002 cover those changes. The upstream audioop deprecation warning remains visible.

max_evals is not total API requests, tokens or RMB; no hard all-role spend cap exists.
No actual model Tool Calling/Simulator/Reflection chain has been validated. The
Layer-1 real task gate must precede a separately approved Layer-2 optimizer gate.
Proposal: ../experiments/M3_LIVE_TEST_PROPOSAL.md. Stop at M3-A.

## Local Git / GitHub closure
Implementation/evidence commit: d43a9ab6000eb558d7bedde55269b76ebdb63321,
branch codex/m3-gepa-offline. It records the tested source hashes above; tests ran
on the audited dirty tree before commit, not on an invented prior commit.
Six M3 Issues #13-18 were created only after checking existing Issues and are
assigned to existing milestone 3. Their bodies now contain checked M3-A criteria,
actual results/evidence paths and local SHA; final authenticated re-read verified
all six remain open with those fields. Open means pending publication/review.
No push, default-branch modification, merge or Release. The final documentation
closure adds no executable code or lock changes, so no redundant test run is claimed.
