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

New major decisions record context, choice, alternatives, evidence and consequences.
Distinguish pinned-source facts from local decisions and unverified runtime assumptions.
