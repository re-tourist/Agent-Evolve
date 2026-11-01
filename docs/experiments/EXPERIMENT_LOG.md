# Experiment log

New semantic-feedback Goal: **incomplete, externally stopped**. See
[partial report](SEMANTIC_STUDY_REPORT.md). semantic-study-002 sent755 requests,
753 returned/2errors; known4,098,392 Tokens/estimatedRMB3.3939484 plus unknown-cost
reserves9.796608. Structured search and new Test are Not run. Previous results below
are historical, not acceptance evidence for this Goal.

Exploratory real GEPA/feedback comparison: **core-sprint-001 complete**, 17 task
evaluations +2 Reflection,306 returned calls, estimatedRMB1.293252. Both Best=Seed;
no demonstrated improvement. Independent final Test9/9 complete, all failures kept.
Historical real API smoke attempts: **2**, returned calls **18**, separately authorized.
M2-A/M3-A have explicitly scripted Mock engineering runs; these are not Agent model scores.

| Run ID | Mode | Purpose | Result / evidence |
|---|---|---|---|
| semantic-study-002 | real_api / new shared5000-request/RMB50 authorization | Semantic analysis +20-task failure pool + larger GEPA search | Provider InternalServerError at755; Basic3 proposals/22 scored+1fault; no new accepted Best; Structured/Test Not run; [report](SEMANTIC_STUDY_REPORT.md) |
| semantic-study-001 | engineering launch / real API0 | New64Steps validation | Local50-step ceiling rejected before send; preserved, then fixed |
| core-sprint-001 | real_api / approved M3-B2→M4-B→M5 | Fixed Train1/6/7, Val8/10, Test5/9/12; GEPA Basic/Structured then independent Test | New candidate1/arm, each rejected; Best=Seed; final success3/3,1/3,2/3 with same prompt. Source0a820f0; [report](CORE_EXPERIMENT_REPORT.md), [validation](../validation/CORE_SPRINT_VALIDATION.md) |
| qwen-task0-002 | real_api / one newly authorized trial | Normal completion with steps32/output1024 | user_stop, official Reward1, DB match; 10 returned calls; [record](M3B12_QWEN_TASK0_002.md) |
| qwen-task0-001 | real_api / one authorized trial | First actual Qwen Agent/User/tool chain | 8 calls returned; max_steps/step_limit; raw official 0, normalized null/excluded; [record](M3B1_QWEN_TASK0_001.md) |
| tau-scripted-evidence-004 | mock / official framework | Verify actual Retail tool → trace → official Reward export | Reward 0, expected for an inspection script; [record](M2A_SCRIPTED_SMOKE.md) |
| fixture-evidence-002 | mock / synthetic fixture | No-key configuration/artifact data flow | Official Reward unavailable; [validation](../validation/M2A_VALIDATION.md) |
| gepa-offline-002 | real GEPA engine / scripted Retail / reflection fake | Seed → official evaluations → local proposal → reevaluation → result | 3 evaluations, official rewards all 0; two candidate texts, Best=seed; [record](M3A_OFFLINE_SMOKE.md) |

M1 install, import, lint and pytest are engineering checks, recorded in
`../validation/M1_VALIDATION.md`; they do not establish Agent performance.
M2-A tests/provenance: `../validation/M2A_VALIDATION.md`. The first actual Qwen
single-task attempts are recorded above; no Task0 repeat occurred in the core sprint. The first
raw official 0 remains a failure for any official benchmark aggregation that includes
that attempt; smoke-only null/exclusion never licenses denominator manipulation.
Historical initial proposal: `M2_LIVE_RUN_PROPOSAL.md`.

M3-A validation: [actual commands and evidence](../validation/M3A_VALIDATION.md).
Exploratory API/fixture and preliminary gepa-offline-001 artifacts are retained in
ignored outputs/runs; the final run above identifies reviewed source hashes.
Synthetic 0-to-1 acceptance is a contract fixture, not a performance experiment.
The original [layered proposal](M3_LIVE_TEST_PROPOSAL.md) is historical. The later
explicit sprint approval authorized the bounded real run above; it has now stopped.
306 current requests and18 historical calls are reported separately, not budget resets.
