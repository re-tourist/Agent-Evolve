# 模板与初始仓库审计

审计日期：2026-11-01（Asia/Shanghai）。初始 HEAD：
`b09786e7ebff300426fe4ca28cb5a2e47b33f35b`；分支 main；origin：
https://github.com/re-tourist/Agent-Evolve。仅 README.md 已跟踪，内容为项目标题；无已跟踪修改。
18 个未跟踪文件与外部模板逐字节相同；另有空 pyproject.toml 和用户规划 v0.2。
规划文件保留原始字节，SHA256：`94a7119c5cad094dbae6518f19610e2895d9f24544c0ec67d0087d84893f86ef`。

安装器帮助/源码仅支持 `--target`、`--dry-run`，不支持选择性安装。
本轮 dry-run 输出 Would add 1 / skipped 18；这与历史 19 文件预览不矛盾，
说明当前磁盘已有 18 文件，无法仅据此断言何时/由谁复制。未实际运行全量安装。
19 项全部读取并比较。没有直接原样保留项：通用文件须重写，专用文件排除。

| 预览文件 | 初始磁盘状态 | 处置 | 理由 |
|---|---|---|---|
| `.agent/plans/000-reproduction-plan.md` | 存在且逐字节一致 | 排除 | 改用 001-m1-foundation.md，不保留复现流程 |
| `.agent/PLANS.md` | 存在且逐字节一致 | 改写 | 保留职责，按 Agent 工程重写 |
| `AGENTS.md` | 存在且逐字节一致 | 改写 | 保留职责，按 Agent 工程重写 |
| `ARCHITECTURE.md` | 存在且逐字节一致 | 改写 | 保留职责，按 Agent 工程重写 |
| `docs/experiments/EXPERIMENT_LOG.md` | 存在且逐字节一致 | 改写 | 保留职责，按 Agent 工程重写 |
| `docs/experiments/EXPERIMENT_TEMPLATE.md` | 存在且逐字节一致 | 改写 | 保留职责，按 Agent 工程重写 |
| `docs/paper/PAPER_SPEC.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `docs/validation/OPTICAL_NUMERICS.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `GOALS.md` | 存在且逐字节一致 | 改写 | 保留职责，按 Agent 工程重写 |
| `prompts/00-repository-audit.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `prompts/01-paper-specification.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `prompts/02-physics-validation-plan.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `prompts/03-minimal-optics-implementation.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `prompts/04-training-smoke.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `prompts/05-reproduce-paper-result.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `prompts/06-independent-review.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `REPRODUCTION.md` | 存在且逐字节一致 | 排除 | 论文/光学专用，不适用 |
| `tools/capture_environment.py` | 存在且逐字节一致 | 改写 | 移除 torch/CUDA/nvidia-smi、路径和工作区清单；仅保留安全元数据 |
| `新建 Text Document.txt` | 不存在 | 排除 | 旧项目路径命令备忘；本地不存在，不引入 |

仅移除已核对相同的模板文件；删除前再次比较字节。保留并重写的 7 项、排除的
12 项合计 19 项，其中 11 个已存在排除项被移除、1 个本来不存在。
`新建 Text Document.txt` 没有创建或删除。外部模板目录不作修改。

## 指令冲突
检查 D:/、D:/AI project/、仓库根及项目内 AGENTS.md/AGENTS.override.md；
只发现根 AGENTS.md，内容是已核对的光学模板。它要求论文/光学复现，与本轮用户
明确的 Agent M1 范围冲突；按用户指令重写。未发现额外 override。
原始文档作为审计证据仍可在外部模板检查，不将光学模板内容归档回项目。
