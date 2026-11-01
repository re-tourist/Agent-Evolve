# Qwen single-task preparation (M3-B, no execution authorized)

Clean baseline 23509a1 on codex/m3-gepa-offline. Read governance, plan, protocol,
M2/M3 code and pinned tau generation/runner source. No user changes present.
Scope: one dedicated entry reusing M2 construction/export, one Beijing Qwen model,
environment-only credentials, bounded calls/timeouts and logs. Keep existing Live
gates and GEPA unchanged. No real request in this task; approval flag is for later.

- [x] Check official model ID, tools, region, Key/base URL and pricing.
- [x] Add narrow single-task preflight/live entry; no generic provider framework.
- [x] Offline tests of limits, credentials/gate, forwarding and actual official runner.
- [x] Record commands/results, proposal and stop pending explicit approval.

Final root 80 passed / 16 opt-in skips; Qwen native offline 3 passed; GEPA core
regression 5 passed / 1 worker skip; seven original official tau tests passed.
Ruff lint/format and diff checks passed. Found/fixed missing official English pack
via sparse checkout, no upstream modification. Initial fixture/temp failures and
upstream Windows warnings recorded in docs/validation/QWEN_PREPARATION.md.
Current model qwen-plus-2025-12-01 explicitly listed in official snapshot docs;
earlier search snippet 2025-07-28 not used. API requests: 0. Await explicit approval.

Risks: remote compatibility/model availability unverified; call cap is not a money
cap. Account balance/alerts may not stop requests immediately. No hard tokenizer or
currency controller is requested. Root/tau/GEPA locks and upstream code stay fixed.
