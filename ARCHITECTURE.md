# Architecture and implementation boundary

## Implemented in M1
`src/agent_evolve/__init__.py` exposes package version metadata only.
`tools/capture_environment.py` writes an allowlisted CPU-only environment snapshot.
pytest/ruff and CI validate the foundation without model credentials.
M1 remains the foundation; M2-A and M3-A additions are described separately below.

## Implemented in M2-A
`baseline.py` owns validated JSON config, frozen Prompt/Policy composition,
offline/mock/live gating, socket denial, fixture backend and normalized artifacts.
`tau_backend.py` reuses official task loading, per-task Retail environment,
LLMAgent system_prompt override, scripted User and official Orchestrator/run_simulation.
No copied scoring/database implementation. `environments/tau` isolates upstream
dependencies from root development and future GEPA. See `docs/M2_RUNBOOK.md`.
Modes: offline = task/Policy preflight, mock = scripted participants, live = always
rejected in M2-A. The construction-only seam configures official Agent/User model
objects, with generation forbidden by tests; it is not an active live runner.
Trace messages/tool fields and original reward details are retained. Missing metrics
are unavailable; infrastructure/simulator/step-limit errors have no normalized task
score. M2 adds no optimizer; M3-A integration is described below. Live approval proposal:
`docs/experiments/M2_LIVE_RUN_PROPOSAL.md`.

## Implemented in M3-A
`gepa_adapter.py` owns split validation, immutable candidate/evaluation evidence and
TauEvaluator. The evaluator sends one validated M2 Config to the original M2 CLI
in a fresh process, checks identities/Policy/RewardInfo, and returns official Reward
plus basic status/tool/Trace references. Failures abort with null project scores.
`optimization.py` runs pinned public optimize_anything with explicit budgets,
train/validation examples, test_set=None and deterministic callable reflection.
It saves all observed candidates (including rejected ones), reflection I/O, official
candidate pool/lineage, result/metadata/eval_log and selected Best. No fabricated
unexposed ancestry. Separate GEPA core and τ environments avoid the full-extra
LiteLLM conflict. No M2 implementation or official Orchestrator/scoring was changed.
Real engine + synthetic tests and real engine + scripted Retail are distinct from
hosted-model experiments. M2/M3 Live remain closed; no M4 feedback algorithm exists.
See `docs/M3_RUNBOOK.md` and `docs/M3_GEPA_AUDIT.md`.

## System boundaries and later-stage intent
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
