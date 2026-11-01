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
- [ ] Narrow offline contracts then commit source/config before new real requests.
- [ ] Real gateA: training failure with auditable semantic evidence and advice.
- [ ] Real gateB: failure diagnostic actually in Reflection -> candidate -> score.
- [ ] Real gateC: multiple train tasks/new candidates and independent validation.
- [ ] Auto M5 after gates; freeze Bests,2Trials/new Test task, deduplicate identical
  selected prompts explicitly rather than pretend identical arms are different.
- [ ] Analyze all outcomes/costs/attribution limitations, two behavior examples,
  publish sanitized evidence and update PR/Issues/CI; stop.

Chosen new split is frozen in examples/semantic_study.json before any request.
Task metadata only informs judge-free eligibility; no target/reference content is
used to choose Test. Test gold/trace never goes to optimization. Scalar Reward is
unchanged; diagnostic compliance is auxiliary and cannot silently affect acceptance.
Baseline pool sampling is shared by arms and rotates failures, flagged ambiguity
and successes for coverage; no fabricated failure. Current-state execution, not
offline tests, must prove A/B/C. If credential/provider/global budget blocks work,
preserve partial results, do not pretend the goal complete.
