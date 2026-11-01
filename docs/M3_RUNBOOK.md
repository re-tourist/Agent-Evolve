# M3-A offline optimization runbook

Read GOALS/architecture/protocol and M3_GEPA_AUDIT first. M2-B has never run;
its live gate is retained. No model service or paid inference is permitted in M3-A.

## Provision isolated GEPA core
From repo root (do not clone again if the expected checkout already exists):
```powershell
git clone --filter=blob:none --no-checkout https://github.com/gepa-ai/gepa.git .cache/gepa-source
git -C .cache/gepa-source sparse-checkout init --cone
git -C .cache/gepa-source sparse-checkout set src tests docs examples
git -C .cache/gepa-source checkout 8c7b697a71977980afc7537dac0881e784eef99f
uv sync --project environments/gepa --frozen
```
Root uv/pytest/ruff and the τ checkout/environment from M2 remain unchanged.
The checked editable source and lock have portable relative paths; runtime rejects
a different SHA, changed tracked GEPA source or another installed GEPA package.
Public source/package provisioning needs network; all actual optimization is offline.

## Run
```powershell
environments/gepa/.venv/Scripts/python.exe -m agent_evolve.optimization --config examples/m3/offline.json
```
Use a new run_id in a config copy for every run. Paths resolve relative to config.
Example uses official Retail train task 0, project validation task 1 (also drawn
from official train), and reserved official test task 5. These are tiny development
subsets, not a sufficient formal experiment. Test is never selected/evaluated or
sent to GEPA/reflection. Split JSON accepts IDs/source pin only, no target states.
GEPA gets dataset=train, valset=validation and test_set=None.
The official loader reads/parses the full local task JSON before filtering IDs;
this is not a filesystem access barrier around test data. No test task, target
state or acceptance criterion is exported to GEPA/reflection by this adapter.

OptimizationConfig reuses M2 Config through baseline_file and changes only candidate
instruction, single-task selection, output location and effective seed. It adds
bounded GEPA options rather than a generic provider/plugin configuration framework.
Default mode is offline; live always refuses before GEPA import, baseline reads
or output creation. No approval flag/environment variable bypasses the gate.

Agent/Simulator in this example are M2 scripts, Reflection is a deterministic local
callable, Judge none (M2 refuses tasks requiring one). Real GEPA chooses/proposes/
evaluates candidates; it is not a mock optimizer. Strict-improvement on these fixed
inspection scripts normally yields equal zeros and retains seed. Synthetic contract
tests separately exercise a changed fixture score and accepted candidate lineage;
neither is model improvement evidence.

## Adapter and artifacts
`gepa_adapter.TauEvaluator(candidate, example)` validates text and split, reserves a
fresh evaluation, calls M2 CLI without a shell, and reads official normalized/raw
artifacts. Identity/Policy hashes, score validity and RewardInfo consistency are
checked before returning `(float_reward, basic_feedback)`. No weighted score,
gold DB state, evaluator criteria or M4 taxonomy is passed as feedback. Unavailable
scores, worker/provider/simulator errors, timeouts or Policy drift abort with null
project scores. Partial evidence is retained; no automatic retry.

```text
runs/m3/<run_id>/
  config.json / baseline_config.json / metadata.json / splits.json
  seed_prompt.json
  candidates/<sha256>.json           # each actually evaluated text, even rejected
  evaluations.jsonl                 # attempted/scored/error events, actual feedback
  evaluations/000001/
    request.json / worker.json / evaluation.json
    m2/                             # original M2 config/Prompt/Trace/Reward/details
  reflection-0001.json               # actual fake input/output; no fabricated reasoning
  gepa/ / gepa_state/                # upstream logs/state from this run only
  gepa_result.json / gepa_metadata.json / gepa_eval_log.json
  candidate_pool.json / best_candidate.json / summary.json
```
The candidate hash is its content version. Actual accepted-pool parent indices come
from GEPA; callback-only rejected ancestry is unavailable. No result overwrites.
State pickle files are local generated artifacts; do not load untrusted state.
Missing usage/cost/lineage remains unavailable. max_evals counts evaluations, not
LLM requests or Token/RMB spend. Worker timeout rejects a result; it is not proof
that every descendant/in-flight provider request or bill has been cancelled.

## Tests and Windows
```powershell
uv run --offline --frozen python -m pytest --basetemp=.cache/pytest-m3 -q
uv run --offline --frozen ruff check .
uv run --offline --frozen ruff format --check .
$env:AGENT_EVOLVE_GEPA_TESTS = '1'
environments/gepa/.venv/Scripts/python.exe -m pytest tests/integration/test_gepa.py -q
```
For the additional actual Retail worker test set AGENT_EVOLVE_TAU_WORKER_TESTS=1
and provision the M2 environment. For τ regressions/candidate-specific isolation,
set AGENT_EVOLVE_TAU_TESTS=1 and use the τ interpreter on test_tau.py and
test_gepa_tau.py. Native Windows permissions may be required for upstream asyncio
socket-pair cleanup; the workers themselves still deny model socket/DNS connections.
CI adds a GEPA-core job with deterministic reflection and no provider SDK; the
actual τ worker opt-in remains separately documented. Remote CI is not run locally.

Actual checks/artifacts: validation/M3A_VALIDATION.md. Next action is review of
experiments/M3_LIVE_TEST_PROPOSAL.md, not starting M3-B or M4.
