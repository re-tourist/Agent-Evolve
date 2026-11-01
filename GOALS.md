# Goals and acceptance

Agent-Evolve is a local-first repository for Agent evaluation, Prompt optimization,
and optionally future data construction and SFT/RL experiments. The sole current
subproject is **GEPA × τ-bench: trace-grounded Prompt optimization for customer-service
Agents**. PROJECT_PLAN.md v0.2 is the design baseline.

## Current scope: M2-A (offline Baseline & Trace)
M1 foundation is retained. M2-A delivers a small validated CLI, configurable Agent
Instruction separated from fixed official Policy, trace/reward artifacts, scripted
fixture and official-framework offline tests, plus a one-task Live proposal.
Live execution remains disabled; approval and reviewed M2-B activation are required.
Mock tests are engineering evidence only. Remote CI is separate from local checks.

## Milestone gates
- M1 Repository Foundation & Codex Governance: reproducible offline foundation.
- M2 τ-bench Baseline & Trace: one authorized real Retail task with isolated state,
  full trace, official Reward and provenance.
- M3 GEPA Optimization Loop: real bounded search with candidate lineage and scores.
- M4 Trace-grounded Structured Feedback: evidence-linked diagnoses and scalar comparison.
- M5 Controlled Experiments & Portfolio Release: frozen splits, matched budgets,
  honest final-test results and reproducible public report.

## Non-goals
M2-A implements no paid run, automatic Prompt search or GEPA integration.
The current project does not rewrite upstream algorithms/benchmarks, build a web
platform, add RAG, voice or multi-Agent execution, or train SFT/RLHF/RL weights.
GPU provisioning and paid evaluation are not foundation requirements. No Agent
performance claim is made.
