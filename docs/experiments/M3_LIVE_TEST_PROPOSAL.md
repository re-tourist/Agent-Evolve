# M3-B layered Live proposal — NOT APPROVED / NOT RUN

Update 2026-11-01: the first single-task provider choice is superseded by
[Qwen Task 0 preparation](QWEN_SINGLE_TASK_PROPOSAL.md). Both require explicit
approval; no real call has run. The historical DeepSeek assumptions below do not
authorize any call or select a provider for future GEPA automatically.

Prepared 2026-11-01 (Asia/Shanghai). Both M2 and M3 live gates remain closed.
This document is neither authorization nor a switch. No provider key is required
for M3-A. User and technical adviser must explicitly approve each layer separately.

## Layer 1 — one genuine Agent task, then stop
- Upstream τ 2.0.0 SHA `da0835f6c67baef58bdda18f2a3b037dfb3a1754`.
- Retail **task 0**, one trial, seed 42, one worker, max_steps 12 / max tool errors 2.
  Task 0 belongs to the official train set. No final test task is used.
- Agent and official UserSimulator: DeepSeek `deepseek-flash`, advertised version
  DeepSeek-V4.1-Flash-1017, non-thinking, requested temperature 0, max_tokens 512,
  per-request timeout 30s, retries 0. These are proposed settings, not verified calls.
- Judge: none for task 0's empty NL assertions/no communicate requirements; preserve
  EvaluationType.ALL and original criteria. No auto-review or Reflection in Layer 1.
  Different tasks can activate default paid judges; do not suppress those components.
- Endpoint `https://api.deepseek.com`, OpenAI-compatible Chat Completions. Proposed
  client route `openai/deepseek-flash` with environment-only API base/key in the
  isolated worker. Client SDK compatibility does not imply an OpenAI-provider call.
  No other provider/fallback is authorized by this proposal.

DeepSeek [documents tool calling](https://api-docs.deepseek.com/zh-cn/guides/tool_calls/).
Its [thinking-mode protocol](https://api-docs.deepseek.com/guides/thinking_mode/)
requires replaying reasoning_content with tools; pinned τ serialization drops that
field. The proposed route explicitly disables thinking through a reviewed allowlist
addition; default thinking must not silently remain enabled. LiteLLM 1.82.6 schemas,
tool_choice, actual function-calling responses and hosted Simulator behavior remain
**unverified**. A no-network fake-transport check is required before any approved call.
M2_LIVE_RUN_PROPOSAL.md records the prior gate; no M2-B run has succeeded yet.

Conditional planning envelope: up to 12 Agent + 12 User requests (24 total), each
<=20,000 input and <=512 output tokens, no retries. That is <=480,000 input and
12,288 output tokens **only if these assumptions are enforced**.

Use official RMB peak cache-miss Flash pricing checked 2026-11-01:
[¥2/million input, ¥8/million output](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/).
Conditional estimate: `480000*2/1e6 + 12288*8/1e6 = ¥1.058304`, round **¥1.06**.
Requested Layer-1 ceiling **¥2**, including in-flight reserve. No Search/Fetch/voice.

Expected evidence: one actual conversation/tool trace, original RewardInfo, config/
data/model/Prompt/Policy hashes, task status, available usage/cost/latency, exceptions
and provider billing reconciliation. Success means a valid trace and official score,
not necessarily Reward 1. Infrastructure failure does not count as Agent failure.
**After Layer 1, stop and present evidence. Do not automatically start Layer 2.**

## Layer 2 — separately approved smallest GEPA loop
Only after Layer-1 technical success and a new explicit approval:
- Same pinned τ and GEPA 0.1.4 SHA `8c7b697a71977980afc7537dac0881e784eef99f`.
- Train task **0**, validation task **1**, one trial per evaluation. Both are
  development selections from official train. Reserved test task **5** is not selected,
  evaluated, used for reflection, or passed via GEPA test_set.
- Agent/User: same proposed DeepSeek route/settings as Layer 1.
- Reflection: DeepSeek `deepseek-flash` via a reviewed callable override replacing
  OfflineReflection. Non-thinking, <=1024 output tokens, timeout 30s, retries 0;
  at most **one** reflection request/proposal. Input <=20,000 tokens is an assumption
  requiring an admission check, not an existing capability.
- Judge none for tasks 0/1 at this pin; criteria/hashes must be rechecked before
  execution. Any nonempty assertion/mandatory judge route stops and resubmits.
- GEPA max_evals **4**, max_proposals **1**, serial/no caching, strict improvement.
  Planned sequence: seed validation, seed train, new candidate train, and candidate
  validation only if accepted. Thus up to **4 Agent task executions**, not four total
  LLM requests. Allowing only one proposal is not an optimization-quality experiment.
- Maximum planning allowance: 96 Agent/User requests plus 1 Reflection request.
  Under the per-call assumptions: task side <=1,920,000 input / 49,152 output tokens;
  Reflection <=20,000 input / 1024 output tokens. Total <=1,940,000 input / 50,176 output.
- Conditional estimate `1940000*2/1e6 + 50176*8/1e6 = ¥4.281408`, round **¥4.29**.
  Requested **separate Layer-2 ceiling ¥6**, including reserve. Layer 1's remaining
  budget never authorizes or automatically transfers to Layer 2.
- Real proposer output may be invalid or produce no improvement; retain all attempts,
  actual candidate lineage when exposed, reflection input/output and original scores.
  No M4 taxonomy/Judge or weighted reward, and no benchmark performance claim.

## Enforcement limitations and activation work
**No all-role hard Token/RMB controller exists in M3-A.** max_evals counts evaluation
calls, not Agent/User/Judge/Reflection calls. GEPA max_token_cost is proposer USD
accounting only, not an aggregate token cap or RMB ceiling. Provider request limits,
token estimators, cancellation and bill reconciliation have not been Live-verified.
Timeouts may leave an in-flight charge; subprocess timeout is not proof all descendant
requests are cancelled. Therefore the prices above are conditional estimates, not
unconditional maximum bills. Do not claim strict cost control.

Before paid execution, either implement/test accepted admission and role accounting
controls (including exact model tokenizer/usage assumptions and in-flight reserve)
or obtain explicit reviewer acceptance of the residual limitation plus any verified
provider account-level quota. Reject unknown/unaccountable spend rather than
automatically retrying. Refresh model alias/prices before approval/execution.

Current entry points are real but refuse Live:
```text
Layer 1: python -m agent_evolve.baseline --config <reviewed_layer1_config>
Layer 2: python -m agent_evolve.optimization --config <separately_reviewed_layer2_config>
```
These placeholders are **not executable approved configs**. Existing mode=live
returns exit 2 before work begins. No `--approved` flag, environment variable or
presence of a model key bypasses either gate. M2-B/Layer-1 activation and M3-B/Layer-2
activation are separate code/review steps; passing Layer 1 is not permission to
enable a Reflection model or start an optimizer.

## Diagnostics, recovery and stopping
Stop on first provider/auth/rate-limit/schema/Simulator fault, ambiguous timeout,
unexpected judge/provider, unknown accounting, changed Policy/task/source identity,
or approaching admitted task/call/token/currency limits. Save null-score failure
events and partial M2 evidence; never return Reward 0 for infrastructure faults.
Check provider bills and the request/task ledger, fix locally and re-propose before
another run. Operator may interrupt the foreground process; never silently resume
a partial run or overwrite a Run ID. Unexpected output is not a reason to tune on test.

Deliverable for Layer 2: genuine Seed→Agent tasks→official rewards/feedback→Reflection
proposal→new candidate→reevaluation→GEPA result with all artifacts. Improvement is
not required; trustworthy end-to-end behavior is. Both layers remain **pending**.
No real API, M3-B, M4 or formal comparison has been executed by M3-A.
