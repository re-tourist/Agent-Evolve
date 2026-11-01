# Decisions

| ID / date | Decision and reason | Evidence / consequence |
|---|---|---|
| ADR-001 / 2026-11-01 | Preserve existing repository, remote and v0.2 plan | Initial HEAD b09786e; plan existed before edits |
| ADR-002 / 2026-11-01 | Rewrite general governance; remove only byte-identical untracked template remnants | TEMPLATE_AUDIT.md; explicit user authorization; no unaudited content deleted |
| ADR-003 / 2026-11-01 | Python 3.12 + uv + pytest + ruff; zero runtime dependencies in M1 | Frozen lock and minimal package; no speculative modules |
| ADR-004 / 2026-11-01 | Upstream pins are integration targets, outside M1 runtime dependencies | UPSTREAM_AUDIT.md; source analysis is not runtime verification |
| ADR-005 / 2026-11-01 | Environment capture uses a standard-library allowlist and exclusive creation | No env dump, local path inventory, GPU probing or model calls |
| ADR-006 / 2026-11-01 | Preserve PROJECT_PLAN.md v0.2 bytes | Historical planning status stays in baseline; execution state lives in current plan/log |
| ADR-007 / 2026-11-01 | Reuse original GitHub Milestones 1-5 and normalize roadmap titles | Final verification found alternate titles after initial empty responses; move six Issues to original M1 and remove only session-created duplicates 6-10 |
| ADR-008 / 2026-11-01 | M2-A uses official manual composition/Orchestrator + run_simulation with scripted participants | Official custom_agent_eval.py pattern; no registry mutation/global Prompt patch; per-task fresh environments |
| ADR-009 / 2026-11-01 | Live is unconditionally closed in M2-A; configuration is not authorization | User requires explicit approval before M2-B; single-task proposal records missing provider/budget activation work |
| ADR-010 / 2026-11-01 | Keep separate locked tau environment tied to validated local source checkout | Avoid M1 dependency churn and future GEPA-full/LiteLLM conflict; pin/source/data identity checked |
| ADR-011 / 2026-11-01 | Exclude infrastructure/simulator/protocol/step-limit failures from normalized task metrics | Keep original upstream RewardInfo/zero in raw evidence; never score infrastructure faults as business failures |
| ADR-012 / 2026-11-01 | M3 reuses M1 GEPA SHA and installs core only in a separate lock/environment | Actual OptimizeAnythingConfig/callable reflection tested without LiteLLM; full-extra conflict remains |
| ADR-013 / 2026-11-01 | Reuse unmodified M2 CLI per evaluation through a serial JSON/subprocess boundary | Official Reward only, fresh state/history, identical Policy; missing/invalid scores abort |
| ADR-014 / 2026-11-01 | Save all observed candidates separately from GEPA accepted pool | Rejected candidates may be absent from GEPAResult; preserve feedback and exposed lineage without inventing parents |
| ADR-015 / 2026-11-01 | Explicit development split and test_set=None; both Live gates closed | Train 0 / validation 1 from official train, reserved test 5 never evaluated; layered M3-B approval required |
| ADR-016 / 2026-11-01 | M4-A uses conservative observation rules with JSON Pointer evidence; basic feedback stays default | Explicit tool flags/binding markers and termination only; Reward failure is not causal evidence, hidden details never exported, no score/model/Policy change |
| ADR-017 / 2026-11-01 | Authorized real sprint reuses Qwen single-task body and GEPA callable seam across existing isolated environments | `experiment.py`, `live_runtime.py`; shared serial400-request/RMB30 estimated stop ledger, phase92/92/216, no dependency/upstream changes |
| ADR-018 / 2026-11-01 | Formal Live optimization/aggregation uses raw official Reward, including step/protocol zeros; infrastructure faults are unscored | Supersedes ADR-011 only for benchmark score handling: old normalized smoke null annotations never remove official failures; three Test truncations retained |
| ADR-019 / 2026-11-01 | Keep strict rejection and identical frozen Best prompts even when final arm scores differ | Both proposals tied Seed at Train7=1; no further proposals under whole-task reserves. All9 Test trials retained, no post-Test tuning or benefit claim |
| ADR-020 / 2026-11-01 | New Goal uses configurable shared5000/RMB50 limits and20/5/10 split; old experiments retained | Direct chat authorization;64Steps/48calls/900s, same model/pins/Policy/tools/Reward; no independent new budgets per phase |
| ADR-021 / 2026-11-01 | Citation validation is necessary but not semantic truth; gate final Test with an inspected supported case and actual failure-to-candidate chain | Development review found false attribution despite correct quotations; same-Qwen second pass may repeat it; no auxiliary score replaces Reward |
| ADR-022 / 2026-11-01 | Preserve unavailable Usage and conservatively reserve error costs without clearing the final Provider stop | One scoped diagnostic-timeout recovery did not retry its Agent task; later InternalServerError stopped all calls; incomplete Goal reported, not completed |

New major decisions record context, choice, alternatives, evidence and consequences.
Distinguish pinned-source facts from local decisions and unverified runtime assumptions.
