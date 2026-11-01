# Qwen Task 0 / one trial — prepared, NOT APPROVED / NOT RUN

Offline acceptance: [commands/results](../validation/QWEN_PREPARATION.md).

2026-11-01. This replaces the DeepSeek choice for the FIRST single-task gate only.
No GEPA Live run is authorized. Existing baseline/optimization Live gates stay closed;
the dedicated qwen_smoke entry defaults to offline preflight and requires both
--live and --approve-single-task for a later explicitly approved request.

## Model and actual calling requirements
Use **qwen-plus-2025-12-01**, Beijing, for both Agent and official UserSimulator,
temperature 0, non-thinking, max_tokens 512, timeout 30s, no retries.
LiteLLM route: openai/qwen-plus-2025-12-01; this invokes Alibaba, not OpenAI service.
Agent needs function calling; the simulator uses official generation and possibly
user tools. Official Task 0 has no NL assertions/COMMUNICATE requirement, so no
Judge request is required; a changed task criterion or unexpected model stops.
Original EvaluationType.ALL, task, Policy, tools and Reward are unchanged.
Pinned tau2 2.0.0: da0835f6c67baef58bdda18f2a3b037dfb3a1754.

GEPA needs an additional Reflection model in a future optimization; Qwen Plus is
the simplest proposed same-provider choice. No real reflection adapter is activated
or tested now. Other tasks may require official Judge defaults from other providers;
this entry supports only task 0 and does not silently remove those requirements.

Official sources checked today:
- [Model capabilities/pricing](https://help.aliyun.com/zh/model-studio/qwen-plus):
  current explicit 2025-12-01 snapshot, Beijing Function Calling; older search
  snippets mention 2025-07-28 but the current snapshot section lists 12-01.
- [Thinking control](https://help.aliyun.com/zh/model-studio/deep-thinking): extra_body enable_thinking=false.
- [Key and region](https://help.aliyun.com/zh/model-studio/get-api-key).
- [Compatibility/endpoints](https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope):
  workspace domains recommended; existing dashscope domain remains supported.

## User setup and exact commands
Create ONE **Beijing (华北2)** standard Model Studio API Key in the Alibaba Bailian
console, enable/access the selected model. Use a dedicated restricted Key/space
where practical. No OpenAI, DeepSeek or Anthropic Key, Coding Plan subscription,
or extra SDK install needed. Existing locked tau environment is reused.

Configure process environment without placing a secret in shell history:
```powershell
$secret = Read-Host 'Beijing DASHSCOPE_API_KEY' -AsSecureString
$env:DASHSCOPE_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
```
Do not send the Key to this chat. New shells need the environment set again.
The entry uses the documented existing Beijing endpoint:
https://dashscope.aliyuncs.com/compatible-mode/v1
No endpoint/provider fallback. If Key/model is unavailable there, stop and review
the console-selected region/workspace; do not retry with a different supplier.

From repository root, safe now (no Key needed, no network):
```powershell
git -C .cache/tau2-source sparse-checkout add data/tau2/multilingual/en
environments/tau/.venv/Scripts/python.exe -m agent_evolve.qwen_smoke
```
The source checkout needs the pinned official English pack for the real User
Simulator. M2's script did not exercise it. The first command may fetch public
Git objects on a new checkout; it makes no model request. Preflight now renders
both participant prompts so a missing pack fails before any paid call.
ONLY after explicit approval, one foreground execution then stop:
```powershell
environments/tau/.venv/Scripts/python.exe -m agent_evolve.qwen_smoke --live --approve-single-task --run-id qwen-task0-001
```
One task ID 0, one trial, seed 42, max_steps 12/max tool errors 2. No loop,
resume, optimizer or batch. Existing Run ID is refused without overwrite.

## Small-run cost controls, not a finance system
Admission cap 24 TOTAL completion attempts shared by Agent/User, including failed
attempts; unexpected model/Judge or first provider error blocks further sends.
SDK/LiteLLM retries zero; no fallback. 180s admission deadline, 30s request timeout:
the deadline is checked before a call, so this is NOT a strict wall-clock kill timer.
Operator can Ctrl+C; timeout/interrupt can leave a billable in-flight call.

Beijing non-thinking input <=128K tier: RMB 0.8/M input and 2/M output tokens.
At 24 calls averaging 5K-20K input and <=512 output, conditional estimate is
RMB 0.121-0.409 (roughly 0.1-0.5 yuan). Not an unconditional maximum: input tokens
are not hard-capped, and larger contexts have higher tier prices (2.4/20 and
4.8/48 RMB/M input/output). No free credits assumed; refresh price/access before run.
Suggested approval envelope: 1 yuan for this small smoke, conditional on these
assumptions and accepted platform controls, not a software-enforced money cap.

Before approval, user checks prepaid balance, model permissions and available
platform quota/alerts/automatic top-up settings. A balance alert is NOT a hard
per-Key spending limit; accounting/stop delays or credit billing can exceed a
small balance. Use available platform limits, avoid an uncapped funded account.
This task intentionally adds no full token/currency controller.

## Outputs and acceptance
runs/qwen/<run-id>/ contains config, Prompt/Policy hashes, task, source/data/Git
identity, call-NNN.json (latency, returned usage/status, no Key), original raw trace
and RewardInfo, normalized 0.json and summary. Missing/unknown provider cost stays
unavailable; do not trust upstream unknown-model zero price as a bill.
API Key injected after upstream request-log construction; raw provider exceptions
withheld. Check trace and bill before sharing/publishing runtime artifacts.

Success: real tool/conversation trace with official reward (need not be 1), usage
where returned, no surprise provider/Judge, admitted calls <=24. Infrastructure
failure has null normalized score and is not an Agent task failure. Stop/review on
fault or context/token truncation; no automatic retry. Preserve partial artifacts.
After this one task succeeds, separately request a GEPA experiment. No auto-next step.
