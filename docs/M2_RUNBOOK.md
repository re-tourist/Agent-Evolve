# M2-A runner and artifacts

No paid model call is permitted in this stage. Root development needs only M1's
`uv sync --frozen --group dev`; `uv` may be `.bootstrap/Scripts/uv.exe` on Windows.

## Minimal no-key fixture
```powershell
uv run --offline --frozen python -m agent_evolve.baseline --config examples/m2/mock.json
```
This is a synthetic Retail-like fixture, not official τ-bench data or reward.
For a repeat, copy the config and choose a new run_id; existing outputs are refused.
Config paths (instruction file, output_dir, tau_checkout) resolve relative to the
config file. Task IDs are explicit and unique; num_tasks must match their count
(1–10 offline/mock only), max_steps 2–50, seed 0–2^32-1; one trial per invocation.
No official Policy field is configurable. Unknown config/model-argument fields fail.

## Optional official environment provisioning — public downloads, no model calls
Run from the project root. If the checkout exists, verify it rather than clone again:
```powershell
git clone --filter=blob:none --no-checkout https://github.com/sierra-research/tau2-bench.git .cache/tau2-source
git -C .cache/tau2-source sparse-checkout init --cone
git -C .cache/tau2-source sparse-checkout set src examples/agents docs data/tau2/domains/retail
git -C .cache/tau2-source checkout da0835f6c67baef58bdda18f2a3b037dfb3a1754
uv sync --project environments/tau --frozen
```
The portable lock targets the expected relative checkout; the backend rejects a
different commit, tracked modification, installed source or data root. Do not
combine this environment with GEPA-full. Source/data are ignored, not vendored.

In a normal Windows PowerShell (see sandbox limitation in the upstream audit):
```powershell
environments/tau/.venv/Scripts/python.exe -m agent_evolve.baseline --config examples/m2/tau_preflight.json
environments/tau/.venv/Scripts/python.exe -m agent_evolve.baseline --config examples/m2/tau_mock.json
$env:AGENT_EVOLVE_TAU_TESTS = '1'
environments/tau/.venv/Scripts/python.exe -m pytest tests/integration/test_tau.py --basetemp=.cache/pytest-m2-local -q
```
Preflight only loads/hashes task and Policy; mock uses a fixed inspection script
and scripted User, actual official tools/evaluator, no LLM. It deliberately does
not solve Retail tasks. A zero official reward on that script is expected and is
not an Agent model baseline. Tasks needing a model Judge are refused, not re-scored.

## Config and Prompt seam
`Config` validates mode/backend/domain, explicit task IDs/count, models, seed,
max_steps and allowlisted generation args: temperature, top_p, max_tokens, timeout,
num_retries (must be zero). Supply exactly one of instruction or instruction_file.
Prompt version is content-addressed by SHA256; policy and composed system hashes
are independent. Official LLMAgent subclass overrides only system_prompt, retaining
the exact official Policy as a separate immutable string. A future optimizer gets
only the instruction field. Hash immutability does not prove a model obeys Policy.
The construction-only `build_live_components` seam verifies Agent/User model IDs
and generation args reach official participant objects. It never runs or generates;
the CLI cannot reach it while Live is closed.

`mode=live` always fails with exit 2 **before backend import/output/network**.
There is no approval flag/environment variable that enables it in M2-A. The proposal
is not authorization; M2-B requires explicit approval and a separately reviewed
activation/budget/provider configuration change. Current CLI is not a live runner.

## Run output (fresh run_id only)
```text
runs/m2/<run_id>/
  config.json             # resolved config, model IDs and parameters
  prompt.json             # instruction/Policy/system text and hashes
  metadata.json           # source commit/dirty, upstream/data hashes, environment, seed, invocation
  <task_id>.raw.json      # original SimulationRun when available; {} in preflight
  <task_id>.json          # schema below; safe error record if execution failed
  summary.json            # task statuses; explicitly no performance claim
```
Normalized fields: task_id/hash, mode/backend, requested models/args, Prompt hash,
messages including user/assistant/tool calls/arguments/results, official_task_reward,
reward_availability, unmodified evaluation_details, termination/status,
excluded_from_task_metrics, available usage/cost/duration, wall_seconds and error.
No custom diagnostic score or failure-interpretation algorithm is implemented.

Infrastructure/timeouts, SDK errors, simulator errors and step limits have no
normalized task score and are excluded. Any upstream zero from such termination
remains in raw/details for inspection. A normally terminated task with reward 0 is
task_failure. Fixture reward, missing usage and missing latency remain unavailable.
Runtime error messages export only category/class; exception text is withheld to
avoid leaking provider secrets. Review traces for PII before publication. Execution
errors retain partial run artifacts and make the CLI return nonzero.

## Validation
```powershell
uv run --offline --frozen python -m pytest --basetemp=.cache/pytest-m2 -q
uv run --offline --frozen ruff check .
uv run --offline --frozen ruff format --check .
```
Root CI runs these no-key checks and skips the explicit upstream integration suite.
Separate opt-in tests above exercise the real installed framework with model-free
participants. Test results and sample artifacts: `validation/M2A_VALIDATION.md`.
