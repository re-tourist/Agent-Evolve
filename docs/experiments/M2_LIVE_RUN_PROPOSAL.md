# M2-B single-task Live smoke proposal — NOT APPROVED / NOT RUN

Prepared 2026-11-01 (Asia/Shanghai). M2-A stops at this document. Do not infer
authorization from the existence of a config, model key or this proposal.

## Exact scope
- τ-bench distribution tau2 2.0.0, SHA
  `da0835f6c67baef58bdda18f2a3b037dfb3a1754`, unchanged Retail text **task ID 0**.
- **One task, one trial (0), seed 42, concurrency 1**. This is an official train
  task, not held-out test; it may later be used only as development evidence.
- Max 12 orchestrator steps, max 2 tool errors. A step is a framework transition,
  not necessarily one model request. No automatic restart, batch or GEPA.
- Task 0 has DB + NL_ASSERTION basis but null NL assertions and no communication
  requirements. Keep EvaluationType.ALL and original criteria. At this pin the
  neutral NL component makes no model call. Judge/review requests expected: **0**.
  If task/hash/criteria changes, stop and resubmit; do not suppress a scoring component.

## Models, provider and compatibility
| Role | Proposed model/provider | Settings |
|---|---|---|
| Agent | DeepSeek `deepseek-flash`, version advertised as DeepSeek-V4.1-Flash-1017 | non-thinking, temperature 0, max_tokens 512, timeout 30s, retries 0 |
| User Simulator | same DeepSeek model via official UserSimulator | same limits; separate usage accounting |
| Judge | None for task 0 | No optional review; do not load default paid Judge |
| Reflection | None | No GEPA |

Provider endpoint: `https://api.deepseek.com`, OpenAI-compatible Chat Completions.
Proposed LiteLLM identifier: `openai/deepseek-flash`; API base/key supplied via
process environment (`OPENAI_API_BASE`, `OPENAI_API_KEY` for this isolated process,
populated locally from the user's DeepSeek account). No credentials in configs,
command arguments, stdout, traces or committed files. No fallback to OpenAI models.

**DOCUMENTED capability, not runtime proof:** DeepSeek officially supports tool
calls, including non-thinking requests with `extra_body={"thinking":{"type":"disabled"}}`.
The pinned τ serializer preserves tool IDs/names/arguments/results but drops
`reasoning_content`. Thinking-mode tool replay requires that field, so do not rely
on DeepSeek's default thinking mode. LiteLLM 1.82.6 routing, τ's generated schemas,
DeepSeek tool_choice and response parsing remain **unverified by live calls**.
Current Config intentionally does not allow arbitrary extra_body; before an
approved smoke, add only the reviewed non-thinking setting and test its serialization
with a fake transport. Do not silently run the current default thinking mode.

Sources checked on preparation date:
[DeepSeek Tool Calls](https://api-docs.deepseek.com/zh-cn/guides/tool_calls/),
[thinking/reasoning replay rules](https://api-docs.deepseek.com/guides/thinking_mode/),
[API endpoint/model naming](https://api-docs.deepseek.com/).
No compulsory other-provider scorer is expected for **this task**. Other Retail
tasks can require official NL (`gpt-5.4-mini-2026-03-17`) or semantic (`gpt-5.5`)
Judges; optional user review defaults to `claude-opus-4-5`. Those are not authorized.

## Planning envelope and RMB cost
Use official Chinese RMB prices directly; no exchange-rate assumption needed.
[DeepSeek price source](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/),
checked 2026-11-01: peak cache-miss input **¥2 / million tokens**, output **¥8 /
million tokens** for Flash. Use peak/no-cache pricing even for a weekend smoke.
Re-check before execution because prices and model aliases may change.

Conservative *planning assumptions*: up to 12 Agent + 12 User requests = **24**
successful requests, no retries, each ≤20,000 input and ≤512 output tokens.
Total envelope: **480,000 input + 12,288 output tokens**.
Estimated upper cost **conditional on these assumptions**:
`480000 × 2 / 1000000 + 12288 × 8 / 1000000 = ¥1.058304`, round to **¥1.06**.
Request a **¥2 total spending ceiling** including reserve, never 24 calls per role
on top of this envelope. No Search/Fetch APIs, voice, Judge or other tools with
provider-side billing are included/allowed.

**LIMITATION — no claimed hard cap:** M2-A has no live spend/token admission
controller, exact DeepSeek token estimator or in-flight monetary guarantee.
max_steps is not an input-token/currency bound. max_tokens is a provider request
parameter whose enforcement is not live-verified; transport retries/timeouts can
make billing ambiguous. ¥1.06 is not an unconditional maximum bill. Live remains
disabled until the reviewer accepts this limitation or requires a tested admission
gate/account-level quota. A human budget approval alone does not activate code.

## Entry point and activation gates
Prepared config: `examples/m2/live_proposed.json`.
```powershell
environments/tau/.venv/Scripts/python.exe -m agent_evolve.baseline --config examples/m2/live_proposed.json
```
**Current behavior: exit 2, LiveNotApprovedError, no backend/model invocation.**
No `--approved` switch or environment flag bypasses this in M2-A.
After explicit user/adviser review, M2-B must separately implement/review activation,
non-thinking request serialization, hosted UserSimulator behavior, timeout/retry
behavior, per-role accounting and agreed admission/budget controls before using
this same entry point for a real smoke. This is pending work, not an implemented
live capability. If the selected provider/model/settings change, resubmit the proposal.

## Outputs and acceptance
Fresh run directory with config, fixed Policy/instruction/system hashes, source/data
identity, model/version/settings, original SimulationRun, normalized task result,
messages/tool calls/arguments/responses, official RewardInfo/details, per-role
available token/cost/latency and summary. Never overwrite the proposed run ID.
Acceptance is one genuine trajectory with official score and explicit failure or
success; **no score threshold** and no performance improvement claim. Missing
supplier usage is unavailable, not 0. Infrastructure/simulator failures are excluded
from business task failure counts, with original upstream data retained.

## Stop behavior to approve
Proposed M2-B: stop on first provider/auth/rate-limit/simulator/protocol failure,
ambiguous timeout billing, unexpected Judge route, schema mismatch, 12-step limit,
24-request envelope, unavailable accounting, or approaching ¥2 ceiling including
in-flight reserve. A configured request timeout is not a guaranteed global kill.
Operator can interrupt the foreground process (Ctrl+C); keep partial artifacts,
check provider billing, and do not automatically retry. Account-level quota, if
available, is supplementary and must be verified rather than assumed.

**Review decision pending:** user/adviser approves or revises task/model/provider,
non-thinking route, assumptions, ¥2 ceiling and enforcement limitations. Until then
paid calls remain 0. Do not start M2-B, expand task count, or enter M3.
