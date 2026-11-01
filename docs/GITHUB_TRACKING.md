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

## M2-A — 2026-11-01
Reused [M2 milestone 2](https://github.com/re-tourist/Agent-Evolve/milestone/2).
Authoritative repository Issue list checked before creation; no existing M2 Issues.
Created the following six Issues, all assigned to M2:

| Issue | Scope | Local M2-A acceptance |
|---|---|---|
| [#7 M2-01](https://github.com/re-tourist/Agent-Evolve/issues/7) | Official interface audit | Source pin, guide/examples, defaults/Judge and Windows evidence recorded |
| [#8 M2-02](https://github.com/re-tourist/Agent-Evolve/issues/8) | Baseline Runner | Offline/mock CLI/config/artifacts; live closed |
| [#9 M2-03](https://github.com/re-tourist/Agent-Evolve/issues/9) | Prompt/Policy separation | Independent text/hashes, instance-level Prompt, isolation tests |
| [#10 M2-04](https://github.com/re-tourist/Agent-Evolve/issues/10) | Trace/Reward export | Actual scripted tool/RewardInfo export, unavailable metrics and fault labels |
| [#11 M2-05](https://github.com/re-tourist/Agent-Evolve/issues/11) | State/offline tests | Root 41 passed; upstream 6 passed; ruff/format/import passed |
| [#12 M2-06](https://github.com/re-tourist/Agent-Evolve/issues/12) | Live proposal | One train task / one trial, documented RMB assumptions and limitations |

Evidence: `validation/M2A_VALIDATION.md`, command JSON, source/data hashes and
`experiments/M2A_SCRIPTED_SMOKE.md`. Issues stay **open pending publication/review**,
following M1's workflow; local completion does not claim remote CI success.
M2 as a whole is not complete: M2-B real model validation is not approved or run.
No new Milestone, automatic merge, release, push or later-stage issue was created.

Local M2-A implementation/evidence commit:
`f342149669b91cc3a4f2d0c1e96f344660e4b52b` (unpushed). All six M2 Issues now
contain checked M2-A acceptance criteria, actual test evidence, file paths and this
local commit; states remain open. This documentation-only closure adds no code.

## M3-A — 2026-11-01
Reused [M3 milestone 3](https://github.com/re-tourist/Agent-Evolve/milestone/3).
Authoritative Issue list checked before creating six missing M3 entries; no new
Milestone or duplicate Issue. All six are assigned to milestone 3:

| Issue | Scope | Local M3-A acceptance |
|---|---|---|
| [#13 M3-01](https://github.com/re-tourist/Agent-Evolve/issues/13) | GEPA audit/dependency pin | Exact public API/source, core-only isolated lock, root/M2 unchanged |
| [#14 M3-02](https://github.com/re-tourist/Agent-Evolve/issues/14) | Evaluator adapter | M2 subprocess, official RewardInfo consistency, no zero for faults |
| [#15 M3-03](https://github.com/re-tourist/Agent-Evolve/issues/15) | Candidate evidence | Seed/evaluated texts/hashes/feedback, rejected proposals, official pool/Best |
| [#16 M3-04](https://github.com/re-tourist/Agent-Evolve/issues/16) | Optimization runner | Real engine offline, split isolation, budget, unique Run ID, Live refused |
| [#17 M3-05](https://github.com/re-tourist/Agent-Evolve/issues/17) | Offline/exception tests | Root 76 passed; real GEPA 6 passed; official tau 7 passed; ruff/format/import passed |
| [#18 M3-06](https://github.com/re-tourist/Agent-Evolve/issues/18) | Live approval proposal | Layer 1 single-task first, Layer 2 separately approved, conditional RMB estimates |

Evidence: `validation/M3A_VALIDATION.md`, command/source-manifest/example JSON,
`experiments/M3A_OFFLINE_SMOKE.md`, and `experiments/M3_LIVE_TEST_PROPOSAL.md`.
Issues remain **open pending publication/review**; M3 as a whole is not marked
complete because no hosted-model validation has been approved/run. Remote CI is
not run; local native/CI-equivalent tests are identified separately. No push,
automatic merge, Release or M4 work.

Local M3-A implementation/evidence commit:
`d43a9ab6000eb558d7bedde55269b76ebdb63321` (unpushed). All six Issue bodies now
contain checked M3-A criteria, actual validation evidence and this SHA. A final
authenticated read verified #13-18 are open, assigned to milestone 3 and retain
the evidence. This closure changes documentation only; it does not authorize Live.

## Core sprint — M3-B2 / M4-B / M5 — 2026-11-01

Reused M3 Issues13–18 and original Milestones3/4/5. Created only missing delivery
Issues [#19 M4 comparison](https://github.com/re-tourist/Agent-Evolve/issues/19)
and [#20 M5 test/publication](https://github.com/re-tourist/Agent-Evolve/issues/20).
No new Milestone or duplicate task management system.

Real source0a820f0, run core-sprint-001: real GEPA generated/evaluated1 new candidate
per arm, both rejected on equal Train7 score1; Best=Seed. Val mean0.5,4 evals/arm,
Train7 only. Independent Test9/9, success3/3,1/3,2/3; all prompts equal, no demonstrated
improvement.306 requests/1,571,250 Tokens/estimatedRMB1.293252, no provider errors.
Three step-limit official zeros remain. All raw logs/credentials stay ignored.

Evidence: `experiments/CORE_EXPERIMENT_REPORT.md`, reviewed scalar/candidate/manifest
JSON, `validation/CORE_SPRINT_VALIDATION.md`. Relevant Issue acceptance/evidence
is updated for review. Branch `codex/core-experiment-sprint` is the authorized
publication target; review remains open, no main merge or Release.

Publication verified: independent branch pushed,
[PR #21](https://github.com/re-tourist/Agent-Evolve/pull/21) open against main.
Issues13–20 were read/updated in place with checked actual-scope criteria and
immutable report/validation links; all remain open pending review. Both offline
GitHub jobs passed on report commitcebe222. No default-branch change or Release.
