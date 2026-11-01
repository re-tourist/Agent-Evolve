# Agent-Evolve — 项目规划总纲（v0.2）

> 状态：Planning / 尚未进入正式开发  
> 仓库：复用已创建的 `Agent-Evolve` GitHub 仓库，不重建、不改名  
> 开发方式：Codex 协助实现；开发者负责技术决策、实验审查与验收  
> 项目定位：面向 LLM Agent 的评测驱动优化与训练实验仓库（当前仅实现 Prompt 优化）

## 1. 愿景与当前范围

**长期愿景**：围绕 Agent 的评测、Prompt 优化、数据构建及后续 SFT/DPO/RL 训练，逐步积累可复现的工程实验。长期方向不是本期交付承诺。

**第一期子项目**：**GEPA × τ-bench — Evaluation-Driven Prompt Evolution for Customer Service Agents**。

业务问题：面对带工具和业务约束的客服 Agent，如何从真实任务执行结果和失败轨迹中生成可信反馈，自动改进其行为指令，并证明改进在独立任务上有效？

第一期必须实现：
1. 运行并复现 τ-bench Retail 文本场景的真实 Agent 基线；
2. 复用 GEPA，实现候选 Prompt → Agent 任务执行 → 官方任务评分 → Prompt 更新的闭环；
3. 实现有证据依据的结构化失败反馈，并与仅使用标量评分的优化进行对照；
4. 留出独立测试任务，输出真实日志、指标、失败分析与可复现说明。

**本期不做**：自研 GEPA、重写 τ-bench、前端平台、RAG、语音、多 Agent、SFT/RLHF 模型权重训练、大规模模型部署。未来增加训练方向时，再根据真实需求抽象共享模块。

## 2. 上游依赖与工程边界

- τ-bench：`sierra-research/tau2-bench`，当前以官方 2.0 文本评测为目标；由它负责 Task、User Simulator、Environment、Orchestration、原生任务验收。
- GEPA：`gepa-ai/gepa`；优先采用当前版本的 `optimize_anything` 及自定义 evaluator，不修改搜索算法源码。
- 两者的**实际版本/Commit SHA、Python 兼容性、API 签名和许可证**，由 M1 核实后锁定。若依赖冲突，可采用两个隔离环境和明确的进程通信边界；不为了简化安装直接大改上游代码。
- 项目本身负责 Prompt 注入、任务包装、执行证据收集、结构化诊断、实验编排、指标与报告。

### 核心数据流

```text
Fixed Task + Domain Policy + Tools
              │
       Agent + Candidate Prompt
              │
      τ-bench Simulation Runner
              │
      Official Reward + Trace
              │
   Evidence-grounded Diagnostic Feedback
              │
    GEPA Optimizer (train/validation loop)
              │
      New Candidate Prompt ──→ 再次运行
              │
      Held-out Test / A-B Report（仅在优化完成后）
```

**原则**：官方 `Task Reward` 是主要优化和报告指标；自定义反馈提供诊断信息，不擅自改变官方任务评分。固定业务政策与可优化 Agent Instruction 分离。测试集不能用于候选生成、反思或选择。

## 3. GitHub Milestones（按当前命名从 M1 开始）

### M1 — Repository Foundation & Codex Governance（项目初始化）
**目标**：把已克隆仓库建设为干净、可测试、可追踪且适合长期 Codex 协作的工程。

- M1-01：审计已有仓库及 `codex-template` 预览清单，建立“保留／改写／不引入”决策表；
- M1-02：选择性迁移通用 Codex 文件，完成根目录 `AGENTS.md`、`GOALS.md`、`ARCHITECTURE.md`、`.agent/PLANS.md`；
- M1-03：添加本总纲、实验协议、决策记录与合适的实验日志模板；
- M1-04：搭建 Python 3.12 + uv + pytest + ruff、`.env.example`、`.gitignore`、最小离线测试、CI；
- M1-05：核对 GEPA/τ-bench 官方版本、许可、运行方式、API 角色及本地兼容性，记录集成风险和下一阶段命令；
- M1-06：创建／整理 GitHub Milestones 与 Issues（有权限则同步到远端，否则输出可执行清单）。

**完成判据**：干净环境可安装本仓库、离线 tests/ruff 通过；无光学/论文复现误导内容；文档职责明确；未执行付费 API；有真实命令和输出记录。

### M2 — τ-bench Baseline & Trace
**目标**：在固定版本与配置上执行 Retail 文本客服基线。

- 跑通少量真实 Agent 任务（先 smoke，再小批量）；
- 支持固定 Policy 与可配置行为 Prompt 的组合；
- 记录任务 ID、上游 SHA、模型配置、对话、工具调用、官方评分与执行异常；
- 验证每次任务的环境与历史隔离，以及 Mock/真实运行标签。

**完成判据**：至少一条真实 API 任务有完整可核查轨迹和官方 Reward，能够复现或明确解释不可复现的来源。

### M3 — GEPA Optimization Loop（第一个可展示 MVP）
**目标**：让 GEPA 在 τ-bench 上真正改进候选 Prompt。

- 跑通官方 GEPA 最小示例；
- 实现 `candidate + task → official_score + diagnostic_info` 适配层；
- 只优化 Agent Instruction，不改 Policy/Tools/Benchmark；
- 控制候选数、任务数、Token/费用预算，保存 Prompt 版本和优化轨迹；
- 完成一次真实小规模搜索与重新评分。

**完成判据**：GEPA 确实调用真实评测、产生新 Prompt，并保存所有必要证据；不把 Mock 成绩当作真实成果。

### M4 — Trace-grounded Structured Feedback（核心个人贡献）
**目标**：提高反馈的可行动性与可核验性。

- 设计失败分类：工具选择、参数错误、工具结果理解、业务政策、沟通结果、未知；
- 为每个诊断附上 Trace/工具结果/状态证据；没有证据则标注 Unknown；
- 处理任务失败与 API/基础设施故障的区别；
- 比较 GEPA + scalar 与 GEPA + structured feedback（固定相同评测预算）。

**完成判据**：输出可核查的反馈样例与人工审查记录，不把参考轨迹当作唯一合法路径。

### M5 — Controlled Experiments & Portfolio Release
**目标**：形成有说服力的公开算法工程作品。

- 固定训练／验证／最终测试任务及模型、Judge、配置；
- 比较 Baseline、GEPA-Scalar、GEPA-Structured；
- 报告任务成功率、失败类型、Token、延迟、费用；必要时做重复试验；
- 对提升、退化及异常案例做分析，公开可复现脚本和结果边界；
- 完成 README、架构说明、报告与 GitHub Release。

**完成判据**：能从 README 复现实验或检查足够证据；明确区分官方分数、自定义指标与探索性结果。

**求职策略**：M2 的真实基线即可展示学习实践；M3 的真实优化闭环是首个正式可展示 MVP；M4/M5 提供差异化深度。实习投递与项目同步进行。

## 4. 本地运行策略

- **Local-first**：Windows PowerShell 本地开发；优先验证原生兼容性，不兼容再考虑 WSL2；不为本项目优先申请 GPU 服务器。
- 本地执行代码、任务编排、日志处理和测试；Agent、User Simulator、GEPA Reflection、可选 Judge 通过受控 API 推理。**本地不等于免费**。
- M1 只运行无 API 的离线测试。M2 先单任务小预算运行，再决定是否扩展。
- 密钥只放在本地环境变量或不追踪的 `.env`；记录模型提供商、模型版本、温度、任务 ID、随机种子、Judge、费用估算及上游 SHA。
- CI 仅运行离线测试、lint、安全基础检查；不触发付费评测。

## 5. 实验可信度约束

1. 官方 Reward 与任何自定义合规、错误归因指标分别记录；
2. 同一任务的各候选评测独立初始化环境，不共用变更后的数据库；
3. 任务异常（网络、限流、模拟器错误）和 Agent 任务失败分别标注；
4. 优化任务与最终测试任务隔离，防止测试信息进入反思反馈；
5. A/B 对照尽量固定模型、Judge、任务集和 GEPA 调用预算，并保留任务级结果；
6. 不使用未经授权的真实客服数据；公开数据、合成数据须如实标注；
7. 性能未提升也应如实报告，不捏造成功率、成本和实验结论。

## 6. 文档与模板治理

现有 `install_template.py --dry-run` 只预览变更，不表示文件已写入。原模板包含光学／论文复现专用内容，**不得全量直接安装作为有效规范**。

- **选择性保留并改写**：`AGENTS.md`、`ARCHITECTURE.md`、`GOALS.md`、`.agent/PLANS.md`、`.agent/plans/`、`docs/experiments/EXPERIMENT_LOG.md` 和实验模板。
- **审查后决定保留**：`tools/capture_environment.py`（必须确认不依赖光学项目路径、GPU 才能运行）。
- **不迁入本项目**：`docs/validation/OPTICAL_NUMERICS.md`、光学实现、物理校验、训练 smoke 等旧 `prompts/` 模板；`docs/paper/PAPER_SPEC.md` 不设为必需文件。
- **重新命名或替换**：`REPRODUCTION.md` 可改为 `docs/RUNBOOK.md`；`000-reproduction-plan.md` 改为 M1 初始化计划；删除误建的 `新建 Text Document.txt`（仅当确认属于模板残留且经用户允许）。
- **新增**：`docs/PROJECT_PLAN.md`（本文件）、`docs/EXPERIMENT_PROTOCOL.md`、`docs/DECISIONS.md`；`README.md` 提供清晰导航。

文档分工：`AGENTS.md` 只写长期不变的 Codex 规范；本文件解释 roadmap；`ARCHITECTURE.md` 解释模块边界；`EXPERIMENT_PROTOCOL.md` 写评测口径；`.agent/PLANS.md` 约束复杂任务的执行计划；实验日志只记录实际执行。

## 7. 初始化目录预期（M1 以最小必要结构为准）

```text
Agent-Evolve/
├── AGENTS.md
├── GOALS.md
├── ARCHITECTURE.md
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── .agent/
│   ├── PLANS.md
│   └── plans/001-m1-foundation.md
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── DECISIONS.md
│   └── experiments/
│       ├── EXPERIMENT_TEMPLATE.md
│       └── EXPERIMENT_LOG.md
├── src/agent_evolve/
│   └── __init__.py
├── tests/
│   └── test_smoke.py
├── tools/
│   └── capture_environment.py  # 审查通过才保留
└── .github/workflows/ci.yml
```

不需要在 M1 就创建空的 `training/`、`feedback/`、`gepa_adapter.py` 或完整实验框架。后续目录随真实实现逐步扩展。

## 8. M1 决策门与风险

- **API/版本风险**：GEPA 的不同文档版本 API 表述不同；必须检查锁定版本源码或运行时签名后再使用，不要凭旧教程猜配置类名称。
- **依赖冲突风险**：τ-bench 与 GEPA 的依赖、平台需求可能不完全兼容；先做约束求解，如冲突隔离进程。
- **评测成本风险**：一次任务可能调用 Agent、模拟用户、Judge 多个 LLM；优化又反复执行任务，必须有硬预算。
- **结果解释风险**：不能把小规模优化或不同版本基准的结果与官方排行榜直接比较。
- **进度风险**：短期内以可运行的单任务闭环为中心，禁止无必要的基础设施扩张。

## 9. Definition of Done

Milestone 只有在以下条件均满足时才可关闭：
- 对应 Issues 的验收条款有可检查证据；
- 实际运行过必要的测试并记录命令与结果；
- 变更有文档、配置与版本记录；
- 没有未说明的 API 成本、数据泄漏或 Mock 冒充真实实验；
- 说明遗留问题与下一 Milestone 的依赖。

> v0.2 为规划初稿。M1 审计后可通过 `docs/DECISIONS.md` 记录微调，避免未经解释地反复推翻整体路线。
