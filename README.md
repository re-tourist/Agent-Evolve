# Agent-Evolve

Evaluation-driven experiments for LLM Agents. 当前唯一正式子项目为 **GEPA × τ-bench**：
基于执行轨迹反馈的客服 Agent Prompt 自动优化。

**Status / 当前状态**：M2-A offline Baseline & Trace. 已实现配置校验、Prompt/Policy
隔离、离线/脚本化 Runner 和 Trace/Reward 导出。真实模型基线、GEPA 和结构化反馈
尚未验证或实现。付费调用 0 次；Live 模式关闭，等待审批及 M2-B 审查。

```powershell
uv run --offline --frozen python -m agent_evolve.baseline --config examples/m2/mock.json
```

这是合成 Fixture；官方 Retail 脚本化运行、独立环境安装及输出格式见
[M2 runbook](docs/M2_RUNBOOK.md)。同一 run_id 不可重复覆盖。

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
network. The snapshot command refuses to overwrite an existing file. The baseline
entry point supports offline/scripted runs only. `.env.example` contains comments
only; no key is needed for M1 or M2-A.

## Roadmap
| Stage | Scope | State |
|---|---|---|
| M1 | Repository Foundation & Codex Governance | See validation evidence |
| M2 | τ-bench Baseline & Trace | M2-A offline; M2-B not approved |
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
- [M2 source audit](docs/M2_UPSTREAM_AUDIT.md), [M2 validation](docs/validation/M2A_VALIDATION.md)
- [Live proposal — not approved](docs/experiments/M2_LIVE_RUN_PROPOSAL.md)
