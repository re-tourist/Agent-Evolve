# Experiment log

Formal LLM benchmark/optimization experiments: **None / Not run**.
Real API smoke attempts: **2**, returned model calls **18** (Qwen task 0, separately authorized).
M2-A/M3-A have explicitly scripted Mock engineering runs; these are not Agent model scores.

| Run ID | Mode | Purpose | Result / evidence |
|---|---|---|---|
| qwen-task0-002 | real_api / one newly authorized trial | Normal completion with steps32/output1024 | user_stop, official Reward1, DB match; 10 returned calls; [record](M3B12_QWEN_TASK0_002.md) |
| qwen-task0-001 | real_api / one authorized trial | First actual Qwen Agent/User/tool chain | 8 calls returned; max_steps/step_limit; raw official 0, normalized null/excluded; [record](M3B1_QWEN_TASK0_001.md) |
| tau-scripted-evidence-004 | mock / official framework | Verify actual Retail tool → trace → official Reward export | Reward 0, expected for an inspection script; [record](M2A_SCRIPTED_SMOKE.md) |
| fixture-evidence-002 | mock / synthetic fixture | No-key configuration/artifact data flow | Official Reward unavailable; [validation](../validation/M2A_VALIDATION.md) |
| gepa-offline-002 | real GEPA engine / scripted Retail / reflection fake | Seed → official evaluations → local proposal → reevaluation → result | 3 evaluations, official rewards all 0; two candidate texts, Best=seed; [record](M3A_OFFLINE_SMOKE.md) |
| None | real GEPA optimization | Not authorized or executed | Not run |

M1 install, import, lint and pytest are engineering checks, recorded in
`../validation/M1_VALIDATION.md`; they do not establish Agent performance.
M2-A tests/provenance: `../validation/M2A_VALIDATION.md`. The first actual Qwen
single-task attempts are recorded above; no third attempt is authorized. The first
raw official 0 remains a failure for any official benchmark aggregation that includes
that attempt; smoke-only null/exclusion never licenses denominator manipulation.
Historical initial proposal: `M2_LIVE_RUN_PROPOSAL.md`.

M3-A validation: [actual commands and evidence](../validation/M3A_VALIDATION.md).
Exploratory API/fixture and preliminary gepa-offline-001 artifacts are retained in
ignored outputs/runs; the final run above identifies reviewed source hashes.
Synthetic 0-to-1 acceptance is a contract fixture, not a performance experiment.
M3-B2 real GEPA remains unapproved/unrun; [layered proposal](M3_LIVE_TEST_PROPOSAL.md).
