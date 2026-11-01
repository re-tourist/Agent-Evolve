# Core experiment sprint: M3-B2 -> M4-B -> M5

User approved the complete plan and real calls: one shared 400-request / RMB30
estimated-spend stop threshold; basic92, structured92, test216 requests. No reset,
no task retry, concurrency1, task32steps/24calls/600s, request1024tokens/30s/retries0.
Start clean189a37c, branch codex/core-experiment-sprint. Read governance, plan,
protocol, actual Qwen/GEPA/tau implementations; retain existing pinned environments.
The latest authorization supersedes old GOALS limits; no new Milestone or Task0 smoke.

Freeze Train1/6/7, Val8/10, Test5/9/12, seed42, same existing seed instruction,
Qwen12-01 Beijing for Agent/User/Reflection, judge-free official tasks. Budget8 task
evaluations/arm, <=2proposals, minibatch1, strict improvement, skip_perfect=false,
no cache/parallel. Stop proposals if fewer than4 metric calls remain. Test is
separate, only after both Best prompts frozen. Never send gold details to GEPA.

- [x] Reusable live task + secure credentials + global serial budget/role guard.
- [x] Live GEPA evaluator/reflection and one continuous entry; offline checks.
- [x] Freeze source/config before paid work; Basic then Structured then9 Test trials.
- [x] All raw official failures retained; analyse real feedback/candidates/costs.
- [x] Sanitize evidence/history; original Milestone Issues, branch push and review PR.

API/permission/network/missing usage/unknown model/loop/global budget stop all sends.
Preserve checkpoints/partial results, no invented score or candidate. Stage request
admission exhaustion preserves Test reserve. No claim of significant improvement.

Preflight evidence: narrow55 passed (1.59s), pinned GEPA synthetic live-contract2
passed(0.56s), original Qwen+Reflection wire tests4 passed(28.53s), shared actual
Retail Task1 scripted/Reflection2 passed(25.24s). Visible upstream warnings retained.
Ruff fixed initial local style issues; fixture string-to-Path/allowed-train-ID
assertion mistakes corrected without changing acceptance semantics. Zero real calls
before freeze. Credential available, all8 tasks judge-free, official split verified.

Executed from clean source0a820f0 with run core-sprint-001. Basic4/8 evaluations,
Structured4/8, each one real new candidate evaluated and rejected on a1-to-1 tie;
both Best=Seed, complete Validation mean0.5, Train coverage7 only. Whole-task
24-call reserves stop both searches before a second proposal. Test9/9 complete:
Baseline3/3, Basic1/3, Structured2/3; all prompts identical, three max_steps zeros
retained. No improvement claim. Requests306/400, Tokens1,571,250, estimatedRMB1.293252,
all Usage reconciled, zero provider errors. No additional real calls after completion.

Published reviewed code/evidence on codex/core-experiment-sprint, PR21 open for
review, no merge/Release. Reused M3 Issues13–18; only necessary M4/M5 Issues19/20
created under original Milestones, all acceptance evidence updated and Issues
left open for user review. Report commitcebe222 GitHub lint-test/gepa-offline passed.
Original raw artifacts preserved; post-run formal score views make diagnostic
pointers resolvable without editing the old smoke null annotations.
