# M1 validation evidence

Date: 2026-11-01 (Asia/Shanghai). Mode: **engineering_check**.
Benchmark runs: None / Not run. Mock Agent runs: None / Not run. Model API calls: 0.
Project source baseline: `b09786e7ebff300426fe4ca28cb5a2e47b33f35b` + M1 working-tree
changes. This record is committed with those changes; it cannot contain its own SHA.
Environment: Windows 11 / AMD64, CPython 3.12.8, uv 0.9.5, pytest 8.4.2,
ruff 0.14.14. No GPU check/training required or executed. Dataset/seed/models: N/A.
Config: pyproject.toml + uv.lock; no evaluation config or model keys used.

## Final offline checks
All rows below actually ran; full stdout/stderr and runtime are retained in
`M1_COMMAND_RESULTS.json`. `uv` in this table denotes the repository-local
`.bootstrap/Scripts/uv.exe`. The explicit repository cache avoids external paths.

| Command | Exit | Seconds | Key output |
|---|---|---|---|
| `uv --cache-dir .cache/uv run --offline --frozen python -m pytest tests/test_smoke.py -q` | 0 | 0.766 | .                                                                        [100%] 1 passed in 0.03s |
| `uv --cache-dir .cache/uv run --offline --frozen ruff check .` | 0 | 0.094 | All checks passed! |
| `uv --cache-dir .cache/uv run --offline --frozen ruff format --check .` | 0 | 0.109 | 4 files already formatted |
| `uv --cache-dir .cache/uv run --offline --frozen python -m pytest --basetemp=.cache/pytest-m1 -q` | 0 | 3.484 | ..                                                                       [100%] 2 passed in 2.35s |
| `uv --cache-dir .cache/uv run --offline --frozen python -c "import agent_evolve; print(agent_evolve.__version__)"` | 0 | 0.203 | 0.1.0 |
| `uv --cache-dir .cache/uv run --offline --frozen python tools/capture_environment.py --output runs/m1-final-check/environment.json` | 0 | 0.829 | Environment snapshot written |
| `uv --cache-dir .cache/uv sync --offline --frozen --group dev` | 0 | 0.078 | Audited 8 packages in 2ms |
| `UV_PROJECT_ENVIRONMENT=.cache/clean-env uv --cache-dir .cache/uv sync --offline --frozen --group dev` | 0 | 0.125 | Audited 8 packages in 2ms |

The two tests verify installed version/Python metadata and environment snapshot
secret exclusion plus refusal to overwrite existing evidence. They do not establish
Agent behavior, benchmark correctness, GEPA optimization or model performance.

## Installation and representative smoke
- `python --version`: exit 0, Python 3.12.8.
- `uv --version`: initially command unavailable; no global uv installed.
- `python -m venv .bootstrap`: exit 0; local bootstrap environment created.
- `.bootstrap/Scripts/python.exe -m pip install uv==0.9.5`: exit 1; configured
  Aliyun mirror wheel failed SHA256 verification. Download was rejected, not installed.
- Retry `... -m pip install --index-url https://pypi.org/simple --no-cache-dir uv==0.9.5`:
  exit 0, uv 0.9.5 installed into .bootstrap only. No hashes disabled.
- `uv lock --default-index https://pypi.org/simple`: exit 0; resolved 8 packages.
- `uv --cache-dir .cache/uv sync --frozen --group dev --default-index https://pypi.org/simple`:
  exit 0; built agent-evolve and installed 8 packages, including pytest 8.4.2/ruff 0.14.14.
- A separate `.cache/clean-env` was provisioned with
  `UV_PROJECT_ENVIRONMENT=<repo>/.cache/clean-env uv --cache-dir .cache/uv sync --offline --frozen --group dev`:
  exit 0, installed 8 packages from cache. Its subsequent
  `.cache/clean-env/Scripts/python.exe -m pytest --basetemp=.cache/pytest-clean -q`:
  exit 0, **2 passed in 0.93s**. The table's final sync rechecks that environment.
- Representative tool smoke wrote `runs/m1-foundation/environment.json` and
  `runs/m1-final-check/environment.json`, each once. Both are ignored local artifacts.
  They record initial commit + platform and allowlisted package versions, no key,
  environment dump, cwd, interpreter path, GPU inventory or remote URL.

## Failures encountered and resolved
1. Sandbox `gh auth status` reported invalid credentials; network-enabled retry
   succeeded with repository access. No reauthentication/global config change needed.
2. `uv run --offline --frozen pytest tests/test_smoke.py -q`: exit 1,
   `Failed to canonicalize script path` in this Windows/sandbox context.
   README/CI use `python -m pytest`, which was executed successfully.
3. Initial metadata test compared literal specifier order, failed because wheel
   metadata canonicalized `>=3.12,<3.13` to `<3.13,>=3.12`. Assertion now compares
   the same required clauses as a set; requirement itself was not changed.
4. Initial full tests: 1 failed/1 error (specifier issue plus sandbox temp directory
   access). Final tests use repository-local `--basetemp`; both tests passed.
5. Initial ruff format check: exit 1, one test required formatting. Ran formatter;
   final check reports 4 files already formatted. No rule disabled.
6. Fresh-env sync initially failed with distribution-cache access denied (os error 5).
   Network-capable execution permission retry, still `--offline`, passed. No upstream
   build/runtime compatibility is inferred from this foundation installation.
7. A local report-generation attempt hit Windows GBK output/decoding errors; explicit
   UTF-8 corrected report generation. This was not a benchmark/test success.
8. GitHub connector failed in transport while creating the third Issue. Authenticated
   gh fallback listed existing issues before creating missing ones; no duplicate Issue.

## Upstream constraint check (expected failure)
Extracted LiteLLM requirements from the two pinned pyproject.toml files into
`.cache/litellm-conflict.in` (contents below), then ran:
`uv --cache-dir .cache/uv pip compile .cache/litellm-conflict.in --offline --python-version 3.12`.
Exit **1**, `No solution found`; resolver concludes requirements are unsatisfiable.

```text
litellm>=1.83.0,!=1.92.0,!=1.92.1,!=1.93.0,!=1.93.1,!=1.94.0,!=1.94.1,!=1.95.0
litellm>=1.80.15,<1.82.7
```

This confirms the direct GEPA-full/τ-bench conflict, not failure of M1 checks.
Isolation architecture and unverified runtime risks are in `../UPSTREAM_AUDIT.md`.

## Not executed / limitations
- No upstream installation, τ-bench task, GEPA optimization, real model request,
  benchmark metric, model-cost measurement or GPU validation.
- Remote GitHub Actions has not run: the local foundation commit is not pushed.
  CI provisions dependencies from public registries, then runs offline checks;
  it contains no model credentials or model evaluation job.
- Local install validates Windows foundation only. Linux CI and native Windows
  upstream integration remain unverified. Dependency provisioning initially needs
  network/cache; offline checks require that provisioning to have succeeded.

## Final diff inspection
The staged diff was inspected. Default `git diff --cached --check` returned exit 2
only for the supplied PROJECT_PLAN.md lines 3-5: each ends in two spaces for
Markdown hard line breaks. The baseline file is intentionally preserved byte for
byte; no whitespace rule or test tolerance was disabled. Running
`git diff --cached --check -- . ':!docs/PROJECT_PLAN.md'` returned exit 0 for all
other files. These formatting notices do not represent failing Python tests.

## M2 entry condition and smallest task
First implement a no-key preflight in a separately pinned τ environment: load exactly
one Retail task and its fixed Policy, emit task ID/content hashes and upstream SHA,
and assert that no model generation function is called. No real task execution yet.
Only after that and explicit per-role/total budget approval, attempt one real task.
