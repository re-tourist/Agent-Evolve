# Agent-Evolve

Evaluation-driven experiments for LLM Agents. 当前唯一正式子项目为 **GEPA × τ-bench**：
基于执行轨迹反馈的客服 Agent Prompt 自动优化。

**Status / 当前状态**：M1 repository foundation. Python package metadata, offline
checks and governance only. Agent baseline, GEPA optimization and structured
feedback are **not implemented**. No benchmark result or paid model call in M1.

## Quick start / 本地启动
Use Python 3.12 and uv 0.9.5. If uv is absent, install it locally in PowerShell:

```powershell
python -m venv .bootstrap
.\.bootstrap\Scripts\python.exe -m pip install --index-url https://pypi.org/simple uv==0.9.5
.\.bootstrap\Scripts\uv.exe sync --frozen --group dev
```

From the repository root, run the following. When using the local bootstrap above,
replace `uv` with `.\.bootstrap\Scripts\uv.exe` (no global installation required):

```sh
uv sync --frozen --group dev
uv run --offline --frozen python -m pytest
uv run --offline --frozen ruff check .
uv run --offline --frozen ruff format --check .
uv run --offline --frozen python -c "import agent_evolve; print(agent_evolve.__version__)"
uv run --offline --frozen python tools/capture_environment.py --output runs/local-check/environment.json
```

Initial provisioning downloads packages; subsequent checks need no model key or
network. The snapshot command refuses to overwrite an existing file. There is no
Agent CLI yet. `.env.example` contains comments only; no key is needed for M1.

## Roadmap
| Stage | Scope | State |
|---|---|---|
| M1 | Repository Foundation & Codex Governance | See validation evidence |
| M2 | τ-bench Baseline & Trace | Planned |
| M3 | GEPA Optimization Loop | Planned |
| M4 | Trace-grounded Structured Feedback | Planned |
| M5 | Controlled Experiments & Portfolio Release | Planned |

长期可探索 SFT/RL；当前不训练模型权重，不重写官方 Benchmark 或 GEPA。
Policy 与可优化 Prompt 分离，训练/验证/测试隔离，所有付费批量运行需预算批准。

## Documentation
- [Goals](GOALS.md), [Architecture](ARCHITECTURE.md), [Agent rules](AGENTS.md)
- [Project plan v0.2](docs/PROJECT_PLAN.md), [M1 ExecPlan](.agent/plans/001-m1-foundation.md)
- [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md), [Decisions](docs/DECISIONS.md)
- [Template audit](docs/TEMPLATE_AUDIT.md), [Upstream audit](docs/UPSTREAM_AUDIT.md)
- [Actual validation](docs/validation/M1_VALIDATION.md), [GitHub tracking](docs/GITHUB_TRACKING.md)
- [Experiment log](docs/experiments/EXPERIMENT_LOG.md), [Template](docs/experiments/EXPERIMENT_TEMPLATE.md)
