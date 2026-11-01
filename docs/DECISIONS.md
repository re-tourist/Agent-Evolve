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

New major decisions record context, choice, alternatives, evidence and consequences.
Distinguish pinned-source facts from local decisions and unverified runtime assumptions.
