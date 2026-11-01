# Core sprint validation — 2026-11-01

Source under real evaluation: `0a820f0a9d12929febb0a9fe2e21e2138f0597d4`, clean.
Pinned upstream source/locks unchanged. Final documentation/CI changes do not
change the code that generated real results. No full historical suite rerun.

## Actual final narrow checks

All commands below executed locally and exited0:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_sprint.py tests/test_qwen_smoke.py tests/test_gepa_adapter.py -q --basetemp .cache/pytest-core-final
# 55 passed in 1.58s
$env:AGENT_EVOLVE_GEPA_TESTS='1'
environments/gepa/.venv/Scripts/python.exe -m pytest tests/integration/test_gepa.py tests/integration/test_sprint_gepa.py -q --basetemp .cache/pytest-core-gepa-final
# 8 passed, 1 skipped in 4.25s
.venv/Scripts/ruff.exe check .
# All checks passed!
.venv/Scripts/ruff.exe format --check .
# 24 files already formatted
git diff --check
# no whitespace errors; Windows autocrlf notices retained
.venv/Scripts/python.exe tools/capture_environment.py --output docs/experiments/core-sprint-001/environment.json
# Environment snapshot written (after live execution)
```

The skipped test is the previously gated real tau integration in test_gepa.py:172;
the GEPA-only environment does not contain tau, as designed. New search-contract
tests run the pinned real GEPA engine with **synthetic** worker scores/reflection;
their score changes are not real model improvements. Offline tests deny sockets.
CI's existing GEPA job now includes the two new sprint contract cases.

## Before the first real request

- Same narrow55 passed1.59s; new pinned-engine synthetic cases2 passed0.56s.
- Real SDK mock-HTTP original-Qwen/Reflection checks4 passed28.53s; final guarded
  official scripted Task1/Reflection transport cases2 passed25.24s. No cloud calls.
  Visible upstream audioop/eventloop warnings were retained, not suppressed.
- Three-role ledger/phase continuity, request401 rejection, fee threshold,
  missing Usage/failure stops, Test admission denial, original official zeros,
  Policy/tool/data identity, Run ID no-overwrite and Reflection text persistence
  covered. Existing isolation tests remain intact; each live task uses a fresh process.
- Corrected local fixture Path/allowed-train-ID assumptions during development;
  no changed acceptance threshold or masked failure. Ruff style fixes only.
- Config-only CLI returned offline_config_only/real_calls0. CSV present/ignored,
  no Git history tracking, Beijing route approved; all8 task metadata judge-free.

## Actual real execution and reconciliation

The one continuous `--live` command in the report exited0. Basic4 evaluations,
Structured4, final Test9. Two Qwen proposals were really evaluated and rejected;
both Best=Seed. Total306 requests (Agent196/User108/Reflection2), all returned,
1,571,250 Tokens, estimatedRMB1.293252. No errors, retries, pending request or
global budget stop. Three official step-limit zeros retained; no infrastructure
error was inserted as a task score. No more requests after the ninth final trial.

The private append-log and all response IDs reconcile306=304task+2reflection.
848 private output files scanned against the exact credential:0 hits. Published
results omit raw customer data/endpoint IDs/auth material. Credential CSV remains
ignored/untracked and its SHA256 unchanged. Historical smoke recorded18/21
artifact hashes remain identical, raw official0/1 preserved.

Actual scalar evidence, candidates and a116-entry private artifact hash manifest:
`docs/experiments/core-sprint-001/`. Review/publish scan covers the outgoing Git
objects and public working files; no raw trace/CSV is intended for upload.
Remote CI results are separate from these local checks and recorded with the PR.
