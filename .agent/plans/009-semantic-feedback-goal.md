# Goal: semantic failure feedback, sufficient GEPA search, independent M5

Objective source: user attachment goal-objective.md (92c9f8ce-aeb6-49b1-9724-9d2dfa2ed49f).
Start clean3c570d0, existing PR21 branch. Preserve previous raw artifacts/source pins:
GEPA0.1.4/8c7b697a, tau2.0.0/da0835f6. No upstream edits or dependency upgrade.

Latest explicit approval supersedes the previous sprint stop: new shared5000
requests/RMB50 estimated threshold, all roles including semantic diagnosis;
Qwen12-01 Beijing, serial, no task retry, default64Steps with bounded calls/time.
No main merge/Release or new Milestone. Existing model API and isolated workers reused.

- [x] Read current goals/architecture/design/protocol and inspect actual pinned API.
- [x] Semantic observable-only view, deterministic observations + Qwen analysis,
  evidence validation, attribution/uncertainty/actionable generalized suggestions.
- [x] Configurable limits/splits,20-task baseline pool, matched failure/success
  sampler,3-example minibatches,40-eval/arm search with multiple real proposals.
- [x] Narrow offline contracts then commit source/config before new real requests.
- [ ] Real gateA: training failure with auditable semantic evidence and advice.
- [ ] Real gateB: failure diagnostic actually in Reflection -> candidate -> score.
- [ ] Real gateC: multiple train tasks/new candidates and independent validation.
- [ ] Auto M5 after gates; freeze Bests,2Trials/new Test task, deduplicate identical
  selected prompts explicitly rather than pretend identical arms are different.
- [x] Analyze available outcomes/costs/attribution limitations and publish reviewed
  partial evidence; final comparison and behavior improvement remain unproven.
- [x] Update existing PR21/Issues16/19/20 with partial results and explicit incomplete
  Goal status; latest offline CI is tracked on PR, not algorithm acceptance.

Chosen new split is frozen in examples/semantic_study.json before any request.
Task metadata only informs judge-free eligibility; no target/reference content is
used to choose Test. Test gold/trace never goes to optimization. Scalar Reward is
unchanged; diagnostic compliance is auxiliary and cannot silently affect acceptance.
Baseline pool sampling is shared by arms and rotates failures, flagged ambiguity
and successes for coverage; no fabricated failure. Current-state execution, not
offline tests, must prove A/B/C. If credential/provider/global budget blocks work,
preserve partial results, do not pretend the goal complete.

## Actual outcome / external stop

Direct chat approval resolved the automatic review's rejection of attachment-only
budget authorization. The first launch stopped locally at0 calls (legacy50-step
validator); fixed to64. semantic-study-002 first diagnostic timed out at30s;
one audited90s recovery reused its completed Task1 and the same ledger, reserving
unknown cost. No Agent task retry. Later source revisions corrected wrong trace
indices, uncited advice, false mock assumptions and terminal-user attribution.
Baseline8 citation-valid findings were reviewed; multiple claims were unsupported.

Provider request755 then raised InternalServerError during Basic candidate3/Task20.
All real sends stopped, root exited1, pending=null.20 baseline tasks9/20 successful;
Basic23 attempts/22 scored/1infra fault,3 proposals (2 complete batches,1 partial),
no accepted new candidate; Seed checkpointVal0.8. Structured and Test Not run.
Known Usage753 responses/4,098,392 Tokens/RMB3.3939484; two unavailable-Usage errors
have conservative reservesRMB9.796608. Ledger stopped at755 with cost bound13.1905564.

A remains unproven (old boolean insufficient); B unexecuted; C partial. No M4/M5
completion claim. Offline follow-up fixes partial-trace persistence and safe status
logging, without replaying the fault. Report/scalar evidence and PR updates preserve
all old runs. Goal stays unachieved; do not clear stop or reset budget to resume.
