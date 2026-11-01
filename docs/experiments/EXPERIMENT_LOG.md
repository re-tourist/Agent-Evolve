# Experiment log

Real LLM benchmark/optimization experiments: **None / Not run**. Paid model calls: **0**.
M2-A/M3-A have explicitly scripted Mock engineering runs; these are not Agent model scores.

| Run ID | Mode | Purpose | Result / evidence |
|---|---|---|---|
| tau-scripted-evidence-004 | mock / official framework | Verify actual Retail tool → trace → official Reward export | Reward 0, expected for an inspection script; [record](M2A_SCRIPTED_SMOKE.md) |
| fixture-evidence-002 | mock / synthetic fixture | No-key configuration/artifact data flow | Official Reward unavailable; [validation](../validation/M2A_VALIDATION.md) |
| gepa-offline-002 | real GEPA engine / scripted Retail / reflection fake | Seed → official evaluations → local proposal → reevaluation → result | 3 evaluations, official rewards all 0; two candidate texts, Best=seed; [record](M3A_OFFLINE_SMOKE.md) |
| None | real_api | No hosted model task or GEPA optimization executed | Not run |

M1 install, import, lint and pytest are engineering checks, recorded in
`../validation/M1_VALIDATION.md`; they do not establish Agent performance.
M2-A tests/provenance: `../validation/M2A_VALIDATION.md`. M2-B is not approved;
proposal: `M2_LIVE_RUN_PROPOSAL.md`.

M3-A validation: [actual commands and evidence](../validation/M3A_VALIDATION.md).
Exploratory API/fixture and preliminary gepa-offline-001 artifacts are retained in
ignored outputs/runs; the final run above identifies reviewed source hashes.
Synthetic 0-to-1 acceptance is a contract fixture, not a performance experiment.
M3-B remains unapproved and not run; [layered proposal](M3_LIVE_TEST_PROPOSAL.md).
