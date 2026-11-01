# Goals and acceptance

Agent-Evolve is a local-first repository for Agent evaluation, Prompt optimization,
and optionally future data construction and SFT/RL experiments. The sole current
subproject is **GEPA × τ-bench: trace-grounded Prompt optimization for customer-service
Agents**. PROJECT_PLAN.md v0.2 is the design baseline.

## Current scope: M3-A (offline GEPA integration)
Update: M3-A complete; current work prepares one Qwen Task 0 smoke only, without
executing it. See docs/experiments/QWEN_SINGLE_TASK_PROPOSAL.md. The dedicated
entry defaults to offline; Live flags require subsequent explicit user approval.
No GEPA Live optimization, M4 or M5 is authorized.

Retain M1 and M2-A. Integrate pinned real GEPA core with the M2 official Reward/Trace
adapter, candidate evidence, explicit train/validation/test boundaries, deterministic
reflection and offline tests. No actual model API chain has been verified in M2/M3.
Both live gates remain closed. M3-B requires staged explicit approval: one real
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
M3-A implements no paid run, model-backed reflection, M4 taxonomy or formal comparison.
The current project does not rewrite upstream algorithms/benchmarks, build a web
platform, add RAG, voice or multi-Agent execution, or train SFT/RLHF/RL weights.
GPU provisioning and paid evaluation are not foundation requirements. No Agent
performance claim is made.
