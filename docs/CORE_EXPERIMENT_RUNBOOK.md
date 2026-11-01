# Bounded GEPA / structured feedback comparison

Authorized sprint: Train 1/6/7, Validation 8/10, Test 5/9/12, seed42. Official
judge-free Retail subset; no Task0 real smoke. Pinned GEPA core0.1.4 source8c7b697a
and tau2 source da0835f6, unchanged isolated locks. Qwen qwen-plus-2025-12-01
Beijing Agent/User/Reflection, temperature0, non-thinking, output1024, request30s,
no retries/concurrency. Task32Steps/24calls; worker subprocess timeout600s.

From repo root, using the existing environments and official sparse checkouts:
```powershell
environments/gepa/.venv/Scripts/python.exe -m agent_evolve.experiment --config examples/core_experiment.json
# REAL calls only under the explicit shared sprint authorization:
environments/gepa/.venv/Scripts/python.exe -m agent_evolve.experiment --config examples/core_experiment.json --live
```
Default reads configuration only and makes zero real calls. Existing run ID is
refused; no automatic resume/retry. Do not copy the config with a new ID to bypass
budget limits. Provisioning instructions remain in M2/M3 runbooks.

Credentials are read from exactly one ignored CSV in docs/ali (key/value or header
format), checked against Git tracking/history and restricted to the Beijing
workspace URL. Never publish the CSV. Parent passes only process environment;
worker request JSON/CLI never contains a Key. No dotenv auto-load or fallback model.

Shared file budget: 400 attempted provider requests, RMB30 estimated cumulative
stop threshold. Basic92 / Structured92 / Test216 request allocations are fixed
for fairness and Test reserve; they are NOT new budgets at phase boundaries.
Before a task, reserve room for24 requests; the unused portion becomes available
within the same phase. A proposal can stop early under this reserve. GEPA task-eval
cap is8/arm, proposals<=2, minibatch1, strict improvement, skip_perfect_score=false,
no cache/parallel, full Validation. A stopper reserves4 metric calls before another
proposal. Train3 is the sampling pool; actual coverage can be smaller and is logged.

Every Agent/Simulator generation is explicitly role-labelled. Reflection uses the
same guard through the pinned SDK in the tau worker. Provider/usage/unknown model/
loop failures stop all further sends. Expected stage admission exhaustion ends that
search using the last full Validation checkpoint; no invented result is returned.
RMB uses per-request Usage and frozen Beijing non-thinking tier prices, ignoring
cache/credit discounts. It is not an invoice or a hard account spend limit; one
in-flight request can cross the threshold. Historical two smokes are separate.

The official raw Reward is the evaluator scalar, including valid zero under
step/protocol/tool-error limits. Infrastructure/budget faults are unscored and
abort; their raw evidence remains. Basic feedback exposes only observable status,
tool names and trace references. Structured adds the existing M4 observations;
no hidden task criteria/target state/free-text bodies go to reflection.

Only after both Best prompts are frozen, Test runs each task with baseline/basic/
structured in that order, each once, even if candidate hashes coincide. No GEPA
test_set evaluation, test-driven editing or new search after Test begins.

Private artifacts: runs/core/<run_id>/{budget.json,budget.jsonl,config.json,
metadata.json,basic/,structured/,frozen_test_prompts.json,test/,summary.json}.
Each worker saves original M2-style full trace/Reward/config, request/response logs,
Prompt/Policy/tool/data identities and actual runtime. Partial results are retained.
Public reports use reviewed scalar tables, prompt hashes and safe excerpts; raw
dialogue/Reflection responses stay ignored. Small samples imply exploratory findings,
not significance or proof of general improvement. No main merge or Release.
