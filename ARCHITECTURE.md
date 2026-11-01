# Architecture and implementation boundary

## Implemented in M1
`src/agent_evolve/__init__.py` exposes package version metadata only.
`tools/capture_environment.py` writes an allowlisted CPU-only environment snapshot.
pytest/ruff and CI validate the foundation without model credentials.
No Agent, runner, evaluator, feedback generator or optimizer is implemented.

## Planned boundaries — not implemented
| Component | Responsibility | Ownership / interface intent |
|---|---|---|
| Agent | Candidate instructions + fixed domain Policy; tool interactions | Custom Agent/factory using official τ-bench API |
| τ-bench | Tasks, Policy, tools, User Simulator, isolated state, orchestration and official Reward | Pinned upstream; tasks/scoring unchanged |
| Evaluator | Candidate + task + config → official score + trace references | Project adapter; infrastructure errors have separate status |
| Feedback | Evidence-grounded diagnosis, Unknown if unsupported | Project; custom diagnostics do not replace official Reward |
| GEPA | Candidate generation, reflection, train/validation selection | Pinned optimize_anything; no algorithm fork |
| Experiment | Splits, budgets, configs, lineage, costs and report | Project; final test isolated until selection is frozen |

Planned flow: fixed task/Policy/tools + candidate → τ-bench runner → official Reward
and trace → evaluator/feedback → GEPA train/validation loop → frozen candidate →
independent test report. A reference trajectory is not the only valid solution.

Model roles: Agent, User Simulator, Reflection Model and optional Judge. Each needs
separate configuration, usage accounting and budget. One task may call several
models. Source pins, extension points and isolation design: `docs/UPSTREAM_AUDIT.md`.
