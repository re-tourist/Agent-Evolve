# Goals and acceptance

Agent-Evolve studies evaluation-driven optimization for LLM Agents. Its current
subproject is **GEPA × τ-bench: trace-grounded Prompt optimization for customer
service Agents**. `docs/PROJECT_PLAN.md` v0.2 is the preserved design baseline;
the execution log and reports describe actual progress.

## Current outcome: M3-B2 / M4-B / M5 exploratory sprint

The explicitly approved `core-sprint-001` is complete and stopped. Real Qwen
Agent/User/Reflection calls exercised pinned GEPA and official Retail scoring.
Both search arms proposed and evaluated one new instruction, rejected its tied
score, and retained Seed. All nine independent Test trials ran. **No optimization
improvement or structured-feedback advantage was demonstrated.** See
`docs/experiments/CORE_EXPERIMENT_REPORT.md` for failures and limitations.

The shared authorization was 400 requests / RMB30 estimated stop threshold;
actual use was 306 requests / RMB1.293252 estimated, with no automatic task retry.
The historical two Task0 smokes are separate and unchanged. No further real run,
new task split, extra trial, budget reset, merge or Release is authorized by this
completion. Any future paid work needs a new reviewed experiment scope/budget.

## Milestone evidence

- M1: repository governance, pinned environments and offline checks.
- M2: real isolated Retail traces, tools and raw official Reward; both Task0
  attempts retained, including the first step-capped official zero.
- M3: actual hosted-model reflection → new candidate → official reevaluation →
  strict selection, with full candidate evidence; Best may remain Seed.
- M4: conservative evidence-linked diagnostics and a real Basic/Structured
  comparison. The sampled successful training task provided little new diagnosis.
- M5: fixed train/validation/test split, nine final trials, reviewed scalar
  artifacts/report and branch/PR delivery for review; no main merge or Release.

## Boundaries

Policy, tools, tasks and scoring belong to pinned upstream τ-bench and remain
unchanged. GEPA optimizes Agent Instructions only. Test traces/hidden criteria do
not enter reflection or selection. Official failures, step truncation and
infrastructure faults stay distinguishable; no result is fabricated or discarded.

No new provider framework, Judge, large taxonomy, web platform, RAG, voice,
multi-Agent system or SFT/RL weight training is included. Future research can
address the observed weak feedback and termination sensitivity after review.
