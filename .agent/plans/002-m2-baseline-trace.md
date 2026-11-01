# M2-A — Baseline & Trace (no paid API)

## Scope and initial state
2026-11-01: clean tree, HEAD afb0e8e, branch codex/m1-foundation, unchanged HTTPS
origin re-tourist/Agent-Evolve. Python 3.12.8, local uv 0.9.5 and uv.lock present;
M1 suite re-run: 2 passed. Work proceeds on codex/m2-baseline-trace.
Read AGENTS, goals, architecture, v0.2 plan, experiment protocol and plan rules.
M1 risks: remote CI/unpushed commits; upstream runtime unverified; GEPA-full and
τ-bench dependency conflict. Do not refactor M1 or install GEPA.

## Work units and gates
- [x] Audit pinned τ 2.0.0 SHA da0835f6c67baef58bdda18f2a3b037dfb3a1754:
  Agent guide/examples, Retail loading, scoring, defaults, traces and Windows.
- [x] Implement small validated config/CLI, instance Prompt/Policy separation,
  offline/mock paths, normalized artifacts and explicit error statuses.
- [x] Reuse official runner/environment in an isolated τ environment; test with
  local scripted participants only. Keep ordinary tests free of upstream/API keys.
- [x] Test config/task validation, trace/reward parsing, output immutability,
  task/DB/history isolation, errors, and fail-closed live mode.
- [x] Record actual checks and mock artifacts; update architecture/goals/ADR/logs.
- [x] Produce one-task/one-trial Live proposal with researched provider/tool/pricing
  and hard-limit limitations. M2-B remains forbidden and awaits explicit approval.
- [ ] Reuse/create six M2 Issues with evidence, inspect diff and safely commit.

## Validation strategy
Run narrow tests then full pytest, ruff check/format and CLI smoke. Run a separate
upstream integration test only if dependencies install safely; record exact pin,
environment, commands, seed, data hashes and failures. Mock rewards are never
benchmark performance evidence. Proposed live path remains disabled during M2-A.

## Decisions / uncertainties
Use official runner APIs without modifying upstream. No unofficial reward or
diagnosis algorithm. Source facts and runtime evidence are labeled separately.
Provider prices/tool support must be verified from official documentation; the
proposal is not an authorization token. No provider API request during M2-A.

## Progress and results
Root suite: 41 passed, 6 explicitly skipped; opt-in official suite: 6 passed.
ruff check/format and package import passed. Final official scripted task 0 gives
Reward 0 with actual tool trace; no model performance claim. Native offline CLI
exits 0; Live config exits 2 before backend import. Windows sandbox cleanup hang
diagnosed and recorded, not marked as successful execution. Missing message costs
are unavailable even when upstream totals default to zero. Tests/fixtures are labeled.
Paid model calls: 0. No M2-B or GEPA execution. Six Issues #7-#12 created under
existing M2; final evidence synchronization and local commit remain.
