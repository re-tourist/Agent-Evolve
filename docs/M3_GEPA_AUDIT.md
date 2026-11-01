# M3-A GEPA source/interface audit

2026-11-01. **SOURCE FACT:** selected package GEPA 0.1.4, MIT, source commit
`8c7b697a71977980afc7537dac0881e784eef99f`. This reuses M1's selected snapshot;
it is not a claim the v0.1.4 release tag contains this newer main-snapshot API.
Python constraint >=3.10,<3.15; project uses 3.12.8. No upstream file modified.

## Exact public surface
From [optimize_anything.py L95](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/optimize_anything.py#L95):

```python
def optimize_anything(
    seed_candidate: str | Candidate | None = None,
    *, evaluator=None, batch_evaluator=None, dataset=None, valset=None,
    objective=None, background=None, test_set=None,
    config: OptimizeAnythingConfig | GEPAConfig | None = None,
) -> GEPAResult: ...
```

- Upstream accepts text, component dictionary or seedless mode. **PROJECT DECISION:**
  accept only nonempty string instructions (<=8192 chars). No dictionary containing
  Policy, no seedless automatic text or user-supplied code/model callable in JSON.
- `evaluator(candidate, example)` returns `(score, info)`; info is a JSON feedback
  dictionary. Upstream also accepts scalar/other legacy forms, but our adapter
  requires finite official Reward and consistent original RewardInfo.reward.
- dataset is train examples; valset selects candidates. We provide separate
  ID/split-only examples and keep final test out of the call (`test_set=None`).
  The official Retail loader parses the local full task JSON before ID filtering;
  only selected train/validation tasks execute. This adapter exports no test target
  or hidden evaluator criteria to reflection; it does not implement file access isolation.
- Upstream optional test_set scores seed and best **after search, outside max_evals**.
  Do not use it as a free evaluation or send held-out acceptance state to reflection.

## Actual OptimizeAnythingConfig wiring
From [oa/config.py](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/oa/config.py)
and [GepaEngine](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/oa/engines/gepa.py):

```python
OptimizeAnythingConfig(
    engine="gepa", max_evals=4, max_concurrency=1,
    output_dir=run / "gepa", run_dir=str(run / "gepa_state"),
    engine_config={
        "engine": {"seed": 42, "parallel": False, "use_cloudpickle": False,
                   "raise_on_exception": True, "cache_evaluation": False,
                   "max_candidate_proposals": 1},
        "reflection": {"reflection_lm": local_callable, "reflection_minibatch_size": 1},
    },
)
```

`engine_config` is GEPAConfig-shaped; nested dictionaries are converted to the
corresponding dataclasses. `reflection_lm` is **not** a top-level GEPAConfig keyword
at this pin, despite one indexed FAQ example presenting that form. Use nested
reflection, verified from actual source/runtime. No M1/M2 upgrade to follow a tutorial.

The default reflection model string is `openai/gpt-5.1`. M3-A always overrides it
with `OfflineReflection.__call__(prompt) -> str`, the documented callable seam also
used by upstream tests. It records actual input/output and proposes fixed text;
it is not an LLM or failure-analysis method. Refiner/merge/model-backed tracking
are not enabled. In-process GepaEngine does not access EvalServer.url; the HTTP
listener is lazy, so the offline loop requires no localhost web service.

## Dependencies / isolation decision
GEPA core declares no runtime dependencies. Real search was verified using core
only, without LiteLLM installed in `environments/gepa`. Set use_cloudpickle=False
to use standard-library persistence. The separate lock includes pytest/project;
no GEPA full extra, hosted SDK, MLflow or WandB installed there.
GEPA-full requires LiteLLM >=1.83.0 while pinned tau requires <1.82.7 (M1 evidence).
The full-extra conflict remains; core-only offline is not the same dependency set.
Keep root and environments/tau locks unchanged. M2 runs in its original environment
via a one-task subprocess, JSON config/result boundary; no duplicated Orchestrator.

## Results and serialization
[GEPAResult](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/core/result.py)
exposes best_candidate, best_idx, best_score, candidates, parents,
val_aggregate_scores, discovery_eval_counts, total_evals, eval_log and metadata.
`to_dict()` serializes the candidate pool/core fields and supports from_dict().
It **omits** eval_log, metadata and eval_server_calls; save runtime fields separately.
The project therefore exports gepa_result.json, gepa_metadata.json, gepa_eval_log.json,
candidate_pool.json and best_candidate.json. Each actual evaluator input is also
saved independently, including rejected candidates absent from the accepted pool.
Accepted-pool parent indices are official lineage. Rejected-candidate parent linkage
not exposed to the evaluator is unavailable; no fabricated chronological ancestry.

## Stopping and error behavior
- New API max_evals bounds serial eval-server calls. Project also admits no more
  than that number of worker attempts. Batch evaluation can overshoot upstream cap
  by batch size minus one; project supplies no batch hook and fixes concurrency 1.
- max_candidate_proposals bounds proposals. Cache is off; each real evaluation
  has its own M2 state/history and saved output. Engine and M2 simulation receive
  the configured seed; hosted determinism remains unverified.
- **max_token_cost is proposer USD cost**, not a token count and not the cost of
  Agent/Simulator/Judge evaluations. There is no all-role hard Token/RMB cap.
  Callable tracking may report 0 cost; that is not a measured provider bill.
- Legacy GEPAConfig uses iteration-boundary metric stopping and can overshoot.
  We use OptimizeAnythingConfig, not the legacy launcher entry point.
- EvalServer internally records a failed call with a placeholder zero for budget
  counting, then re-raises. We require raise_on_exception=True and abort the run;
  project failure events have score=null and no Best Candidate is reported.
  Infrastructure failures must never become optimization task Reward 0.

## Evidence boundary
**ACTUALLY VERIFIED:** fixed API/result roundtrip, real GEPA search using local
reflection and injected deterministic fixture scores, exact small eval budgets,
error propagation, and real M2 Retail subprocess feedback with official Reward.
Separate native τ tests verify unchanged Policy/tools and fresh DB/history.
**MOCK ONLY:** reflection content, synthetic score changes and scripted Agent behavior.
**UNVERIFIED:** any hosted model chain, real Prompt improvement, all-role budget
enforcement and formal controlled comparison. No M3-B or M4 executed.
