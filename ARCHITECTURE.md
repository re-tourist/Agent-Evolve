# Architecture and implementation boundary

## Reviewed English text research protocol (in progress)

`tau_protocol=reviewed-en-text` restricts task selection to the English pack's
reviewed50 IDs, loads the official language binding and uses build_text_orchestrator
for Persona/CallContext/environment/User construction. Only Agent Instruction is
replaced; resolved language guidance and fixed Policy/tools remain. Actual context
and effective system prompt are saved. Registry mode remains for old reproduction.
The34 judge-free tasks have frozen18/6/10 research splits; Qwen Simulator and partial
population differ from a full official text-v1/default-Simulator leaderboard run.

Semantic workers extract observable facts first, then attribute control and propose
conditional interventions with limits. Literal evidence checks are not semantic
truth; unsupported advice abstains. Same-model reasoning is not an independent gold
Judge. Official Reward remains the only search score. A real supported failure
Episode→actual Reflection→changed candidate→official scoring chain gates final Test.
Both arms use paired seed42/43 Validation and native GEPA strict selection; perfect
minibatches skip useless proposals. Identical selected prompts share Test measurements
explicitly. No Test evidence enters search or feedback.

Run ledgers inherit prior requests/cost/reserves with immutable snapshots and one
successor marker, never reset authorization. One same-config baseline reschedule can
reuse completed reviewed Episodes after a bounded5xx stop; original failed attempt
and all raw scores stay recorded. Final research acceptance is still unproven.

Audit correction: explicit 'agreement is not completion' instructions occur in the
pinned Voice scaffolds, not the ordinary Text scaffold. Text's generic completion
rule has not prevented Qwen from emitting STOP with confirmations. Simulator prompts
remain unchanged; this is a protocol limitation, not a reason to rewrite Reward.

## Semantic-feedback Goal: implemented path, incomplete real acceptance

`study.py` reuses the existing task worker/evaluator/public GEPA optimizer. It
loads configurable official judge-free splits, builds a baseline failure pool,
shares a deterministic failure/success sampler across arms and exposes40-eval
search caps. `semantic.py` adds observable-only projection, nine semantic labels,
literal evidence checking, attribution/uncertainty and reusable advice. Qwen
analysis and conditional second-pass review run in the existing tau worker, with
all four roles counted by the same dynamic5000-request/RMB50 ledger.

Raw responses, preliminary/reviewed findings and effective prompts are retained
privately. Uncited advice and unreviewed historical findings are stripped before
Reflection. A second same-model request is not an independent gold Judge and does
not replace manual semantic review or official scoring. Policy/tools/data hashes
remain fixed; Test cannot enter optimization. A/B/C artifact checks plus an
inspectable reviewed semantic case gate final testing.

Actual semantic-study-002 stopped on a Provider InternalServerError after755
requests.20 baseline tasks and partial Basic search exist; Structured/held-out
Test do not. Citation-valid development findings included wrong causal claims,
so this is not accepted as a complete reliable business diagnosis engine.
See `docs/experiments/SEMANTIC_STUDY_REPORT.md`.

After the stop, offline-only fixes retain partial trajectories on future worker
exceptions, use nonzero worker failure status and save safe HTTP status metadata.
They have mock-transport tests; no new Live run verifies those fixes yet.

## Current real execution path (core-sprint-001)

`experiment.py` provides the authorized continuous Live entry. `qwen_smoke.py`
keeps its original single-task CLI and exposes the same official execution body
for fresh serial task workers. `optimization.optimize_live()` uses pinned public
GEPA with `LiveEvaluator` and Qwen callable Reflection in the existing tau worker;
legacy baseline/standalone optimizer Live gates remain closed.

`live_runtime.py` owns secure local CSV/environment injection and the one serial
JSON/append-log budget shared across Agent, Simulator and Reflection. Whole-task
admission protects Test reserves; official raw zeros remain scores, while
infrastructure/global-budget faults abort unscored. No upstream or provider
framework fork was added. JSON writes are atomic for this serial process model;
the ledger is not a concurrent service or a cloud billing guarantee.

Real engine + real Qwen candidate evaluation and all9 held-out Test trials are
verified. Both proposals tied their Seed and were rejected, so all Test prompts
are identical. Structured feedback added little information on the successful
sampled training task. See `docs/experiments/CORE_EXPERIMENT_REPORT.md`; this is
integration evidence and exploratory outcomes, not demonstrated improvement.
The following sections record the stages that established this path.

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
hosted-model experiments. Baseline/optimizer Live remain closed; M4-A adds the
optional feedback described below.
See `docs/M3_RUNBOOK.md` and `docs/M3_GEPA_AUDIT.md`.

## Implemented in M4-A
`feedback.py` is a pure normalized-trace to diagnostic-JSON function. It recognizes
explicit tool error/binding markers and termination observations; failed Reward
never establishes a specific cause. Evidence uses message/field JSON Pointers.
No hidden evaluation_details, target state, raw text or reference sequence is
exported. `feedback_mode=structured` optionally adds this JSON to TauEvaluator info;
basic remains default and official Reward/optimizer/Policy are unchanged. Existing
split/admission guards still apply. No Judge or causal failure classifier added.
See `docs/M4_FEEDBACK.md`; no real Agent failure rates or improvement established.

## System boundaries and later-stage intent
Single-task preparation adds `qwen_smoke.py`: reuse M2 official participant
construction, runner and normalization; Beijing Qwen only, task 0 / one trial,
24-call shared guard, 30s requests, no retries and environment-only credentials.
Default is offline preflight. Separate explicit Live opt-in is prepared for later
approval, never executed during preparation. Original baseline/optimizer gates
remain closed. No provider framework or dependency upgrade is introduced.

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
