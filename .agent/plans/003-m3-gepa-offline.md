# M3-A — GEPA offline integration

## Scope / audited baseline
2026-11-01: clean tree at eea3bfb, origin re-tourist/Agent-Evolve unchanged;
M2 commits f342149/eea3bfb present. Branch codex/m3-gepa-offline.
Read governance, v0.2 plan, protocol, M2 audit/runbook/validation, Runner/adapter/tests.
Initial regression: Python 3.12.8 / uv 0.9.5, 41 passed / 6 opt-in skips.
M2 hosted-model behavior and hard currency/token control remain unverified.

## Integration plan (submitted before implementation)
Keep GEPA source target 8c7b697a71977980afc7537dac0881e784eef99f; no floating upgrade.
Reuse M2 Config/execute/Prompt/export and official τ runner unchanged. A small
evaluator validates candidates, invokes a separate τ process, returns official
Reward plus basic trace feedback, and aborts on unavailable/invalid task scores.
Separate GEPA environment, explicit split manifest, deterministic reflection fake,
per-evaluation immutable directories and candidate ledger. Never pass test_set to
GEPA. Save public result fields plus unavailable markers for inaccessible lineage.

## Observable work units
- [x] Audit pinned GEPA config/evaluator/result/reflection/budget source; lock dependencies.
- [x] Implement evaluator, candidate evidence and minimal offline runner/CLI.
- [x] Verify real GEPA engine with deterministic callable reflection; use synthetic
  contract examples separately from actual Retail scripted official rewards.
- [x] Verify M2 Prompt/Policy/tools/history and task/DB state isolation, errors,
  repeated run IDs, limits, and unconditional Live rejection; run M2 regressions.
- [x] Record actual artifacts/commands/source identity and update project docs.
- [x] Submit layered M3-B proposal only; verify/create six M3 Issues with evidence.
- [ ] Inspect diff, commit safely and stop. No push/default-branch change or Release.

## Verification and limits
Narrow unit tests first, then root pytest/ruff/import and opt-in native upstream
tests with socket/DNS denial. Native Windows permissions may be needed for upstream
async client cleanup (M2 evidence); this never enables Live. A metric-call limit
is not an API request, token or RMB cap. No synthetic score is an official Reward.
No inference from a scripted trajectory to actual LLM performance. No M4 taxonomy.

## Progress / decisions / outcome
Implementation and offline validation complete. Root: 76 passed / 13 opt-in skips;
all opt-in cases executed separately: real GEPA 6 passed, official tau 7 passed
(one upstream audioop warning). Ruff check/format and import passed. CI-equivalent
GEPA core: 5 passed / 1 intentional tau-worker skip; remote CI not run.

Final actual CLI run gepa-offline-002: real GEPA engine, deterministic reflection
fake, official M2 Retail subprocess; three official rewards all 0, two candidate
texts, one proposal rejected and Best remains seed. Synthetic 0-to-1 acceptance
exists only in contract tests. Actual trace/candidate/result artifacts retained;
portable extract, source/artifact hashes and commands in docs/validation/M3A_*.

GEPA core stays isolated; root/M2 locks and upstream code unchanged. Six M3 Issues
#13-18 assigned to existing milestone 3; open pending publication/review. Layered
Live proposal submitted, both layers unapproved. Paid/real model calls: 0.
