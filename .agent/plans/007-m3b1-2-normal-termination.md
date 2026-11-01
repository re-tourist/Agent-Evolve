# M3-B1.2: one newly authorized task, qwen-task0-002

Initial clean d17e435 on codex/m3b1-qwen-task0; work on separate branch.
User authorizes exactly one new real task: same Qwen/Task 0/trial/Prompt/Policy/tools/
official scoring; steps 32, output 1024, calls 24, timeout 30, no retries/concurrency,
overall process deadline <=600s. Budget reference RMB1, not a hard currency limit.

- [x] Freeze all first-run artifact hashes; inspect actual step flow / length finish.
- [x] Minimal limit changes, explicit raw official Reward sidecar and observed final DB.
- [x] Narrow offline guard/transport/preflight checks; reject unsafe config.
- [x] One exclusive launch marker and temporary CSV credential/Beijing route; never repeat.
- [x] Analyze actual outcome/Reward/DB/dialogue/usage/M4; preserve first run and stop.

Result: user_stop / raw official1 / DB match / 5 action checks match, 10 successful
model returns, no length finish. 53,736 input +1,865 output; RMB0.0467188 estimate,
supplier invoice unavailable. Observed final DB exchange requested. M4 reports
normal participant stop only. No third task, GEPA, M4-B or M5. Guard tests4 and
offline transport tests3 passed; no full-suite rerun. First18 artifacts unchanged.

First-run observation: 12 counts participant/environment transitions, not just LLM
calls. Last exchange tool result is flushed before max_steps stops next turn.
Message10 has finish_reason=length, no tool_calls: natural-language reply truncated,
not an observed tool-argument truncation. 180s admission can block a longer 24-call
run; raise admission to600 but enforce whole subprocess600 including imports.
Raw official0 remains authoritative. Smoke normalized null is only an engineering
annotation and must never remove official failures from a formal benchmark denominator.
