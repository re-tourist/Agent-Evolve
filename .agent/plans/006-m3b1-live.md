# M3-B1: one explicitly authorized real Qwen task

User authorizes ONE Retail task 0 / trial 1, qwen-plus-2025-12-01 Agent/User,
24 total calls, 12 steps, 30s requests, zero retries, qwen-task0-001. No second
task even on error; no GEPA, benchmark, provider/model/region switch or extra budget.
Initial 01729ea, codex/m4a-structured-feedback; only untracked user credential CSV.

- [x] CSV untracked now and in history; add docs/ali/ ignore (.env already ignored).
- [x] Parse CSV locally without printing secret; never modify original bytes.
- [x] Offline preflight / Task 0 scoring and bounded-entry checks.
- [x] One exclusive launch marker, ephemeral child environment, CSV Beijing workspace
  endpoint override in this process only. Capture/redact stdout/stderr before saving.
- [x] Read original artifacts, usage, official Reward and M4 diagnostics; safe report.
- [x] Verify no secret in staged/tracked artifacts, preserve CSV; stop without retry.

Outcome: exactly one launch / 8 returned requests (Agent 6 / User 2), 5 successful
tool executions including exchange. max_steps causes raw official Reward 0 and
normalized null/excluded step_limit; not a valid business failure metric. Tokens
42,210 input + 1,717 output, RMB 0.037202 usage estimate, supplier bill unavailable.
M4 reports observed max_steps only. No second task or GEPA. Preflight passed;
4 narrow guard tests passed, no full suite repeated. Runtime secret scan clean.
Reviewed 18 runtime artifact hashes / 4 source hashes; repo/runtime/staged full-key
matches all 0. CSV unchanged and untracked/ignored. Result record and safe scalar
evidence only are committed on codex/m3b1-qwen-task0. No push or further execution.

CSV format is key/value rows, not a header table. Workspace endpoints explicitly
identify cn-beijing; current smoke default is the shared Beijing endpoint. Use
CSV's openAiCompatible URL by local process override (metadata records actual URL),
without changing production code or region. No separate auth/test call is made.
API Key exists only in loader memory and child environment, never command arguments.
Real billing remains account-side; usage-derived RMB estimate is not actual invoice.
