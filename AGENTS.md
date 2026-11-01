# Agent-Evolve engineering contract

- Before work read `GOALS.md`, `docs/PROJECT_PLAN.md` and `ARCHITECTURE.md`.
  For substantial tasks follow `.agent/PLANS.md` and keep a checkable ExecPlan.
- Stay within the current Milestone. Inspect existing work; prefer minimal,
  reversible changes and never overwrite unaudited user files.
- Reuse official libraries; pin versions and verify APIs. Never alter benchmark
  tasks, tools, Policy or official scoring to increase reported results.
- Separate fixed business Policy from GEPA-optimizable Agent Instructions.
  Keep train/validation/test isolated; test traces must not enter optimization.
- Distinguish source facts, engineering decisions, inferences and unknowns.
  Record conflicting sources rather than silently choosing an interpretation.
- Distinguish Mock, real API runs, infrastructure faults and Agent task failures.
  Engineering smoke checks are not benchmark performance evidence.
- Never expose secrets or automatically launch costly evaluations. Paid batch
  runs require explicit user-approved model/task/token/cost budgets and stop rules.
- Each Issue needs inspectable acceptance evidence. Run narrow tests then smoke
  checks; never mark failing or unexecuted tests passed. Inspect `git diff`.
- Follow `docs/EXPERIMENT_PROTOCOL.md`; preserve results with unique run IDs.
  Log major architecture changes in `docs/DECISIONS.md`. Do not automatically
  expand into later Milestones.
