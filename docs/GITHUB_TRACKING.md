# GitHub tracking

2026-11-01: authenticated read/write access confirmed. Initial responses appeared
empty, but final verification revealed original Milestones 1-5 with alternate titles.
Reused those originals, normalized their titles to the requested roadmap, and
removed only this session's duplicate Milestones 6-10 after moving the six Issues
to original M1. Final state: exactly five Milestones and six M1 Issues. Issues were
re-listed after a connector transport failure before creating missing entries.
The existing repository/remote were reused; no repository was created.

## Milestones
- [M1 — Repository Foundation & Codex Governance](https://github.com/re-tourist/Agent-Evolve/milestone/1) — open (GitHub numeric ID 1).
- [M2 — τ-bench Baseline & Trace](https://github.com/re-tourist/Agent-Evolve/milestone/2) — open (GitHub numeric ID 2).
- [M3 — GEPA Optimization Loop](https://github.com/re-tourist/Agent-Evolve/milestone/3) — open (GitHub numeric ID 3).
- [M4 — Trace-grounded Structured Feedback](https://github.com/re-tourist/Agent-Evolve/milestone/4) — open (GitHub numeric ID 4).
- [M5 — Controlled Experiments & Portfolio Release](https://github.com/re-tourist/Agent-Evolve/milestone/5) — open (GitHub numeric ID 5).

## M1 Issues
All six Issues are assigned to M1 (GitHub milestone number 1). Each contains explicit
acceptance criteria and evidence paths. They remain **open pending publication and
review**; local evidence does not claim remote CI passed. No later-stage work started.

- [#1 M1-01 Audit repository and template scope](https://github.com/re-tourist/Agent-Evolve/issues/1) — acceptance evidence: `docs/TEMPLATE_AUDIT.md`.
- [#2 M1-02 Establish Codex governance and scope boundaries](https://github.com/re-tourist/Agent-Evolve/issues/2) — acceptance evidence: `AGENTS.md`, `GOALS.md`, `ARCHITECTURE.md`, `.agent/PLANS.md`, `.agent/plans/001-m1-foundation.md`.
- [#3 M1-03 Document project plan and experiment governance](https://github.com/re-tourist/Agent-Evolve/issues/3) — acceptance evidence: `docs/PROJECT_PLAN.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/DECISIONS.md`, `docs/experiments/EXPERIMENT_LOG.md`, `README.md`.
- [#4 M1-04 Initialize Python package and offline CI](https://github.com/re-tourist/Agent-Evolve/issues/4) — acceptance evidence: `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, `docs/validation/M1_VALIDATION.md`.
- [#5 M1-05 Verify pinned GEPA and tau-bench integration feasibility](https://github.com/re-tourist/Agent-Evolve/issues/5) — acceptance evidence: `docs/UPSTREAM_AUDIT.md`, `docs/upstream-source-manifest.json`.
- [#6 M1-06 Establish GitHub milestone and issue tracking](https://github.com/re-tourist/Agent-Evolve/issues/6) — acceptance evidence: `docs/GITHUB_TRACKING.md`.

Creation used the connected GitHub plugin for initial Issues, and authenticated gh
for Milestones/missing Issues because the plugin has no Milestone tool and its
Issue transport failed. No fallback draft is needed: all requested tracking objects
exist. Full local foundation evidence: `validation/M1_VALIDATION.md`.

Foundation source/evidence commit: `8094da4ec7df87d564322eeaac500051d3cf750b`
(local only). The Issues record local acceptance evidence and remain open for
publication/review. No automatic push, release, Issue closure
or paid run was performed. M1 stays open for the owner's publication/review workflow.
