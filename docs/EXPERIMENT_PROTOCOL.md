# Experiment protocol

## Data and official scoring
Freeze upstream SHA, task files/hashes, task IDs, domain and split manifest before
optimization. Keep train, validation and final-test IDs disjoint. Reflection sees
train evidence; validation selects candidates; final test is used only after
selection. Never route test traces into reflection or tuning. Reset environment,
database and conversation state for every candidate/task/trial. Do not modify
official tasks, tools, fixed Policy or Reward. Report official task Reward and
custom diagnostic metrics separately. Subset scores are not leaderboard reproduction.

## Modes and failure accounting
Label each run `mock`, `real_api` or `engineering_check`. Distinguish completed
Agent task failures with official reward from provider/infrastructure failures,
simulator errors, cancellations and budget exhaustion. Missing scores are not zeros
or silently dropped successes; report denominators, exclusions and retry policy.
Mock runs establish interfaces only. Seed does not ensure hosted-model determinism.

## Provenance and artifacts
Use a unique run ID and fresh output directory; never overwrite evidence. Record
timestamp/timezone, project commit and dirty state, exact command, config/hash,
upstream SHAs, hardware/software/environment snapshot, data hashes/split IDs,
seed/trial IDs, Prompt/Policy hashes, ancestry and candidate selection rule.
Preserve conversations, tool arguments/results, reward breakdowns and diagnosis
evidence locators after secret/PII review. Never log environment secrets.

## Models and budget
For Agent, User Simulator, Reflection Model and optional Judge separately record
provider, exact model/version, temperature/decoding settings, token usage, latency,
pricing source/date, currency, estimated/actual cost. Judge is supplementary unless
the pinned official evaluator requires it; log rubric/version without replacing
official scores. A task may require multiple paid model roles.
Paid batches require explicit approval for providers/models, task/trial counts,
concurrency, call/token/currency limits, bounded retries and stop conditions. Reserve
budget for in-flight calls. GEPA metric-call limits do not bound total multi-role
spending. M1 paid budget is zero; no model call is authorized by initialization.

## Fair comparison
Baseline, GEPA-Scalar and GEPA-Structured use frozen tasks/models/evaluator,
matched evaluation budgets and validation-only selection. Report task-level scores,
counts, uncertainty for repeats, failures, latency, costs and regressions. Unsupported
diagnoses are Unknown. Negative results remain results. Use the experiment template.
