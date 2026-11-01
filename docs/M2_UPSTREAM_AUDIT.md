# M2-A τ-bench interface audit

2026-11-01, source facts pinned to **tau2 2.0.0**, commit
`da0835f6c67baef58bdda18f2a3b037dfb3a1754` (same target as M1).
No upstream file changed. SHA/tracked-tree checks run before importing the backend.
M1's GEPA-full/LiteLLM conflict still applies; GEPA is not installed or used here.

## Sources read and interfaces selected
All links below refer to the fixed official commit:

- [Agent Developer Guide](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/agent/README.md):
  HalfDuplexAgent defines initial state and next-message methods. LLMAgent already
  handles model calls, tool messages and system state, so subclass only its
  `system_prompt` property for candidate instructions. Never mutate its global prompt.
- [minimal_text_agent.py](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/examples/agents/minimal_text_agent.py):
  documents factory registration and `run_single_task(TextRunConfig, task, seed=...)`.
  **Documentation discrepancy:** its header says no API keys are needed while the
  implementation calls `generate` with a real model. A mock *domain* is not a mock
  *LLM*. Read only; this example was not executed.
- [custom_agent_eval.py](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/examples/agents/custom_agent_eval.py):
  supports manual official environment/Agent/User/Orchestrator composition and
  `run_simulation(..., evaluation_type=EvaluationType.ALL)`. M2-A uses this public
  path to supply entirely scripted participants without modifying the registry.
  A construction-only seam also wires configured official LLMAgent/UserSimulator
  instances; a test forbids both generation functions and never calls run().
- [Retail environment](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/domains/retail/environment.py):
  `get_environment()` loads a new RetailDB each time (or deep-copies an explicit DB).
  Our adapter calls official `build_environment("retail")` per task. No project DB
  reset implementation. `get_tasks("retail", task_ids=...)` validates IDs; adapter
  preserves requested order and hashes each Pydantic-serialized task.
- [runner/simulation.py](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/runner/simulation.py):
  returns SimulationRun with original `reward_info`, `messages`, termination,
  duration and available usage/cost. `model_dump(mode="json")` is our raw export.
  Project schema is additive, not a reimplementation of Results or official scoring.
- [official evaluator](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/evaluator/evaluator.py):
  ALL combines components according to reward_basis. Premature termination can get
  upstream reward 0: project excludes infrastructure/simulator/protocol/step-limit
  errors from task metrics, retaining the original reward only in raw/details.
  We do not replace official scoring with success inferred from dialogue.
- [environment evaluator](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/evaluator/evaluator_env.py):
  constructs separate predicted/gold environments for replay and comparison.
  Reference actions are evaluator evidence, never the scripted Agent's solution.

## Defaults and hidden cost routes — source facts
From [config.py](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/config.py):

| Role / setting | Pinned upstream default |
|---|---|
| Agent / User Simulator | `gpt-4.1-2025-04-14`, temperature 0 |
| NL assertion judge | `gpt-5.4-mini-2026-03-17`, reasoning effort low |
| Semantic communication judge | `gpt-5.5`, reasoning effort low |
| Optional user-simulator review | `claude-opus-4-5` |
| Steps / errors / concurrency / seed | 200 / 10 / 3 / 300 |
| Trials / simulator timeout | 1 / None |

Do not inherit these as approved choices. M2-A uses no model, max_steps 12,
sequential tasks and trial 0 (one trial). Agent/User model identifiers in mock
configs are requested metadata, never evidence those models ran.
Task 0 is in the official train split. Its basis includes DB and NL_ASSERTION,
but `nl_assertions` is null and `communicate_info` is empty; NL evaluation returns
a neutral component without a call. Task 2 has an actual NL assertion and is
refused in mock mode. No basis or assertion is removed to avoid a paid Judge.
The communication scorer defaults to semantic judging; do not switch to substring
scoring for cheaper live runs. Optional auto-review is not invoked by our manual path.

## Trace fields and unavailable values
Official `ParticipantMessageBase` includes role/content/tool_calls, `usage`, `cost`,
generation_time_seconds and timestamps when supplied. ToolMessage retains call ID,
response and error. `agent_usage` is primarily populated for audio sessions; for
text, per-message `usage` is the useful source. M2 preserves both without inventing
totals. Missing data uses JSON null plus an availability label, not fabricated 0.
Upstream get_cost may sum absent message costs to 0; normalized cost stays null
unless all participant message costs exist. Original framework totals remain in raw.
Reported `duration` and project wall_seconds have different measurement boundaries.

## Actual Windows evidence and limits
The separate `environments/tau` uv project resolves the official core with LiteLLM
1.82.6; no voice/all extras. Root M1 dependencies/lock remain unchanged. The lock
uses the expected local checkout; backend additionally requires its exact Git SHA,
clean tracked tree, installed source path and data root to match. The data manifest
contains hashes of Retail source files; it is persisted per run, not guessed.

**ACTUALLY VERIFIED, no model:** native Windows imports/data loading, independent
Retail DB instances, Agent histories, Prompt/Policy composition, official
Orchestrator + evaluator on scripted tasks 0/1 and repeated task 0. Socket/DNS
outbound calls are denied inside offline/mock runs. A fake SDK exception test
checks error classification without contacting a provider.

**Runtime limitation:** under Codex's restricted Windows sandbox, LiteLLM exit
cleanup hangs while creating a local asyncio socket pair. A faulthandler stack
located `async_client_cleanup.py → asyncio → socket._fallback_socketpair.accept`.
Native-permission runs of the same offline tests exit normally. This is a local
sandbox condition, not proof of hosted-model compatibility. No os._exit, upstream
patch, warning filter or weakened test was used to claim success.

**UNVERIFIED:** DeepSeek/LiteLLM tool schema interoperability, hosted User Simulator
behavior, actual token accounting and all real task performance. Upstream text
serialization discards `reasoning_content`; DeepSeek thinking/tool replay therefore
needs special care. The proposed first run uses non-thinking mode, which requires
a reviewed allowlisted configuration addition in M2-B; current live execution is closed.
