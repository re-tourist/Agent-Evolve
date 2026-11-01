# Experiment log

Real LLM benchmark/optimization experiments: **None / Not run**. Paid model calls: **0**.
M2-A now has explicitly scripted Mock engineering runs; these are not Agent model scores.

| Run ID | Mode | Purpose | Result / evidence |
|---|---|---|---|
| tau-scripted-evidence-004 | mock / official framework | Verify actual Retail tool → trace → official Reward export | Reward 0, expected for an inspection script; [record](M2A_SCRIPTED_SMOKE.md) |
| fixture-evidence-002 | mock / synthetic fixture | No-key configuration/artifact data flow | Official Reward unavailable; [validation](../validation/M2A_VALIDATION.md) |
| None | real_api | No hosted model task or GEPA optimization executed | Not run |

M1 install, import, lint and pytest are engineering checks, recorded in
`../validation/M1_VALIDATION.md`; they do not establish Agent performance.
M2-A tests/provenance: `../validation/M2A_VALIDATION.md`. M2-B is not approved;
proposal: `M2_LIVE_RUN_PROPOSAL.md`.
