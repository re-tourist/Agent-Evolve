# Official upstream audit — 2026-11-01

Scope: public official repository metadata and pinned source only. No upstream
Agent or optimizer was executed, no upstream dependency bundle installed, and no
model call made. Facts below are **SOURCE FACT** unless labeled otherwise.
`upstream-source-manifest.json` records exact source URLs and SHA256 hashes.

## Integration target pins
| Item | GEPA | τ-bench |
|---|---|---|
| Official repository | https://github.com/gepa-ai/gepa | https://github.com/sierra-research/tau2-bench |
| Selected main snapshot SHA | `8c7b697a71977980afc7537dac0881e784eef99f` | `da0835f6c67baef58bdda18f2a3b037dfb3a1754` |
| Commit UTC | 2026-10-31T19:40:38Z | 2026-10-30T05:37:05Z |
| Source package version | 0.1.4 | 2.0.0 (distribution `tau2`) |
| Latest GitHub release observed | v0.1.4, 2026-07-15 | v2.0.0, 2026-10-20 |
| Python constraint | >=3.10,<3.15 | >=3.12,<3.14 |
| License | MIT | MIT |

**DECISION:** select the full SHAs above, not floating `main`, for the next
integration attempt. Package version/release labels do not mean release-tag code
and the selected main snapshot are identical. M1's uv.lock covers only this
repository's foundation dependencies; upstream source targets are pinned here and
their transitive environments must be locked separately before actual experiments.

Sources: [GEPA metadata](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/pyproject.toml),
[τ-bench metadata](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/pyproject.toml).
MIT license files at the same pins have SHA256
`10c47467a961feb40adf3294fe27dd9cba79d4d1b7cf27173b1c34586d4126c3` (GEPA)
and `e67c5aa0074dfcaefd3c3a1aedb94cb539234aecd15d5a972574e3200e6252fe` (τ-bench).
Preserve upstream notices when redistributing code. Dataset/provider terms require
separate review before public experiment artifact release; MIT is not a provider grant.

## Actual optimize_anything interface
Verified by parsing the selected source (no library import):

```python
def optimize_anything(
    seed_candidate: str | Candidate | None = None,
    *,
    evaluator: Callable[..., Any] | None = None,
    batch_evaluator: Callable[..., Any] | None = None,
    dataset: list[Any] | None = None,
    valset: list[Any] | None = None,
    objective: str | None = None,
    background: str | None = None,
    test_set: list[Any] | None = None,
    config: OptimizeAnythingConfig | GEPAConfig | None = None,
) -> GEPAResult: ...
```

`Candidate` represents a component-to-text dictionary; a plain string is also
supported. Evaluator returns `(score, info)` (or a scalar with empty info), where
higher score is better and `info` is free-form feedback. With dataset/valset use
`evaluator(candidate, example)`; single-task mode uses `evaluator(candidate)`.
At least evaluator or batch_evaluator is required. Batch mode consumes candidate/
example pairs and returns aligned results. We plan to pass official Reward as score
and supported diagnostic/trace references as info; this adapter is **not implemented**.

`OptimizeAnythingConfig` is the current surface; legacy `GEPAConfig` dispatches
through `gepa.gepa_launcher`. Import from `gepa.optimize_anything`. The config source
defines `engine="gepa"`, `max_evals=100`, `max_token_cost=None`, `max_concurrency=8`,
`output_dir`, `run_dir` and `engine_config`. For controlled runs explicitly override
budgets and concurrency; do not accept defaults as an approved cost budget.
GEPA-specific reflection options belong under `engine_config` on the new surface.
No executable optimization example is provided in M1 to avoid accidental calls.

**API discrepancy:** Context7's indexed documentation presents the older
`GEPAConfig` surface without `batch_evaluator`/`test_set`/`OptimizeAnythingConfig`.
The selected source explicitly supports them. Use the selected source, not a mixed
version tutorial. Another source inconsistency: the docstring says a budget must be
set, but implementation merely warns if both bounds are None. Project governance
must enforce its own approved limits.

`max_token_cost` caps proposer/optimizer spending, not Agent/User Simulator evaluator
spending. `test_set` scoring occurs after optimization **outside the search budget**
and scores both seed and optimized candidate. **DECISION:** keep final test outside
the optimizer call and run a separately budgeted, frozen evaluation later. Do not
send held-out test traces as feedback.

Source anchors:
[function and semantics, L95 onward](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/optimize_anything.py#L95),
[configuration, L26 onward](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/oa/config.py#L26).

## τ-bench Agent and runner extension points
- [LLMAgent L54 onward](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/agent/llm_agent.py#L54):
  constructor accepts `tools`, `domain_policy`, `llm`, `llm_args` and
  `additional_stop_tool_names`. `system_prompt` is a property combining instruction
  and Policy; constructor has **no general candidate_prompt parameter**. Planned
  extension: subclass this property using an instance candidate instruction while
  preserving domain_policy; do not mutate global AGENT_INSTRUCTION across runs.
- [Registry.register_agent_factory L112](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/registry.py#L112):
  `(factory, name, task_filter=None, metadata=None)` where factory receives
  `(tools, domain_policy, **kwargs)`. Register before invoking the runner in the
  same process; an unmodified external CLI will not know project registrations.
- [runner/build.py L100](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/runner/build.py#L100)
  resolves the factory and passes model config/task/audio kwargs. Planned factory
  must filter/consume relevant kwargs rather than blindly forward all to LLMAgent.
- [runner/batch.py L364](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/runner/batch.py#L364):
  `run_single_task(config: RunConfig, task: Task, *, seed=None,
  evaluation_type=EvaluationType.ALL, save_dir=None, ..., auto_review=False, ...)`
  builds the orchestrator, runs simulation, returns SimulationRun with reward_info.
  `run_domain(config)` is the high-level batch entry (L1232).
- [runner/simulation.py L20](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/runner/simulation.py#L20)
  calls official `evaluate_simulation`; preserve it and report Reward separately
  from diagnostic labels. Review/other LLM-backed scoring may add cost depending
  on selected tasks/settings. Turn off optional auto-review unless budgeted.
- `tau2.run` re-exports the layered runner; its flat `run_task`/`run_tasks` signatures
  are compatibility shims. Prefer `tau2.runner`/configuration-based calls at this pin.

## Compatibility and installation strategy
Python 3.12 is in both supported ranges. **Proven constraint conflict:** GEPA's
`full` extra requires `litellm>=1.83.0` (with excluded versions), whereas τ-bench
requires `litellm>=1.80.15,<1.82.7`. The intersection is empty. GEPA core declares
no dependencies, so this is a `[full]` conflict, not a claim that all possible
minimal installations conflict. A minimal custom-LM route remains **UNKNOWN**.
The conflict is also checked by the local resolver; see M1 validation evidence.

**DECISION — default isolation:** separate Python 3.12 environments, one for
τ-bench text/core and one for GEPA `[full]`; independent lockfiles. Do not install
voice/all extras for Retail text. Keep M1 root dependencies unchanged.

The following are **future provisioning commands, not executed in M1**. Direct Git
pins identify source; an integration stage must also save resolved transitive locks:

```powershell
uv venv --python 3.12 .venv-tau
uv pip install --python .venv-tau/Scripts/python.exe "tau2 @ git+https://github.com/sierra-research/tau2-bench.git@da0835f6c67baef58bdda18f2a3b037dfb3a1754"
uv venv --python 3.12 .venv-gepa
uv pip install --python .venv-gepa/Scripts/python.exe "gepa[full] @ git+https://github.com/gepa-ai/gepa.git@8c7b697a71977980afc7537dac0881e784eef99f"
```

Upstream τ-bench README's official development path is clone → `uv sync` (text/core),
optional extras for voice/dev. Benchmark data paths must be explicitly provisioned
from the matching checkout/version; a pip-installed wheel alone is not proof that
Retail data discovery works. In M2 verify task loading and official CLI help before
writing real-run commands. Native Windows integration is **not yet verified**;
WSL2 is a fallback only after a demonstrated blocker. GEPA full may bring native
wheel/platform requirements; do not bypass its explicit version exclusions.

## Process boundary — design only, verifiable next stage
Use versioned JSON requests containing run/candidate IDs, instruction text/hash,
fixed Policy hash, task ID and approved config reference. A τ worker owns task
loading, fresh state, Agent construction and official evaluation; return status,
official_reward (nullable), reward breakdown, trace paths/hashes and usage per role.
GEPA evaluator calls that worker and surfaces trace-grounded feedback. Keep keys in
worker environment only; no credentials in IPC, request JSON or stdout.

Verify later with a local Mock roundtrip, schema/version checks, timeout/error
propagation, distinct task states, matching Policy hash, process restart and budget
accounting. Do not pass Python objects/pickles across environments. JSON IPC and
state isolation are proposed architecture, **not implemented/tested in M1**.

## API roles and risk
| Role | Purpose | Budget risk |
|---|---|---|
| Agent | Tool decisions and customer responses | Multiple turns/tool retries per task |
| User Simulator | Simulated customer responses | Additional model calls per turn and trial |
| Reflection Model | GEPA candidate generation from feedback | Repeated optimization proposals; separate cap |
| Optional Judge/review | Supplementary diagnosis or evaluator-required LLM scoring | Hidden extra calls; explicitly inspect task/evaluator configuration |

M1 makes zero model calls. No model/provider selection or paid batch is approved by
this audit. Approval and hard per-role/total budgets precede real M2 evaluation.
