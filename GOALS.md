# Goals and acceptance

Agent-Evolve is a local-first repository for Agent evaluation, Prompt optimization,
and optionally future data construction and SFT/RL experiments. The sole current
subproject is **GEPA × τ-bench: trace-grounded Prompt optimization for customer-service
Agents**. PROJECT_PLAN.md v0.2 is the design baseline.

## Current scope: M4-A (offline trace diagnostics)
Active authorization update: implement the approved continuous M3-B2 -> M4-B -> M5
sprint, with one shared400-request/RMB30 estimated budget and fixed3/2/3 split.
This supersedes the older no-next-task restrictions below only within that sprint.
See docs/CORE_EXPERIMENT_RUNBOOK.md; do not add Task0 smoke or expand the budget.
M3-A and Qwen single-task preparation are retained. Add four small evidence-linked
diagnostic types and optional structured GEPA feedback using the same official
Reward. No reference tool path, hidden target or test trace enters reflection.
M3-B1.2 update: a second separately authorized Qwen task-0 trial ended normally
with official Reward 1. The first step-capped raw 0 is retained, never silently
excluded from official benchmark denominators. See docs/experiments/M3B12_QWEN_TASK0_002.md.
No third task, GEPA Live optimization, M4-B or M5 is authorized. Dedicated entry
still defaults to offline; next real optimization needs separate approval.

Retain M1 and M2-A. Integrate pinned real GEPA core with the M2 official Reward/Trace
adapter, candidate evidence, explicit train/validation/test boundaries, deterministic
reflection and offline tests. One actual Agent/User/tool chain is verified, but no
real GEPA reflection/optimization is verified; task 0 has one normal Live completion.
The original baseline/optimizer Live gates remain closed. M3-B requires staged approval: one real
Agent task first; only after review, separately approve the smallest real GEPA loop.
Synthetic score changes and scripted trajectories are engineering evidence only.

## Milestone gates
- M1 Repository Foundation & Codex Governance: reproducible offline foundation.
- M2 τ-bench Baseline & Trace: one authorized real Retail task with isolated state,
  full trace, official Reward and provenance.
- M3 GEPA Optimization Loop: real bounded search with candidate lineage and scores.
- M4 Trace-grounded Structured Feedback: evidence-linked diagnoses and scalar comparison.
- M5 Controlled Experiments & Portfolio Release: frozen splits, matched budgets,
  honest final-test results and reproducible public report.

## Non-goals
M4-A adds no paid run, model-backed reflection, large taxonomy or formal comparison.
The current project does not rewrite upstream algorithms/benchmarks, build a web
platform, add RAG, voice or multi-Agent execution, or train SFT/RLHF/RL weights.
GPU provisioning and paid evaluation are not foundation requirements. No Agent
performance claim is made.
