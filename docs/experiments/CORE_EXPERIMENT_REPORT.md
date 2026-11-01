# Core sprint — M3-B2 / M4-B / M5

2026-11-01；Run ID `core-sprint-001`；模式 **real_api**。本轮已经结束，不再发送请求。

**结论：真实 GEPA 集成已验证，但没有产生更优 Best，也没有证明 Structured Feedback
带来收益。** 两组各真实提出、评估一个不同于 Seed 的候选，因训练分数同为 1 而拒绝；
三组最终 Prompt 相同。9/9 独立 Test 已完成，全部失败与截断均保留。

## 1. 冻结规格与证据边界

执行源码：`0a820f0a9d12929febb0a9fe2e21e2138f0597d4`，所有任务 metadata 均为此提交、
dirty=false。报告与 CI 的后续提交没有改变这次运行源码。

| 项目 | 固定值 |
|---|---|
| GEPA | 0.1.4 / `8c7b697a71977980afc7537dac0881e784eef99f`，core-only |
| τ-bench | 2.0.0 / `da0835f6c67baef58bdda18f2a3b037dfb3a1754` |
| Agent / User / Reflection | `qwen-plus-2025-12-01`，北京既有业务空间 |
| Judge | 无；依据任务元数据排除非空 NL assertions / COMMUNICATE 任务 |
| 生成 | temperature=0，非思考，max_tokens=1024，timeout=30s，SDK retries=0 |
| 任务 | 单 Trial，32 Steps，最多24次 Agent/User 调用，串行独立子进程600s |
| Train / Validation / Test | `1,6,7` / `8,10` / `5,9,12`，seed=42 |
| GEPA | max_evals=8/组，提案≤2，minibatch=1，strict improvement，skip_perfect_score=false |
| GEPA 其他 | 关闭缓存/并行，完整2任务验证，test_set=None |
| 预算 | 共享400次请求 / ¥30累计估算停止阈值；Basic92、Structured92、Test216 |

划分在请求前固定，按官方 train/test 和无需 Judge 的元数据规则选取，不依结果筛选。
Task0 不参与。本报告仅覆盖无需 Judge 的小规模 Retail 子集。
业务 Policy、Tools、任务、官方评分及两份上游源码未修改；依赖锁未升级。
每次任务重建环境、Agent/User 状态，Policy/Tools/数据哈希在所有运行之间一致。

运行环境为 Windows / Python3.12.8；GEPA、τ 各用已有隔离环境。τ 环境
LiteLLM1.82.6、OpenAI SDK3.42.0；使用 OpenAI 兼容协议并不意味着调用 OpenAI 模型。
[环境快照](core-sprint-001/environment.json) 在运行后由 allowlist 工具采集；不是硬件性能测试。

## 2. M3-B2：真实 Basic 优化

真实数据流：Seed → 官方 Validation → Train7评分 → Qwen Reflection → 新候选
→ Train7重新评分 → GEPA严格拒绝 → 已完整验证的 Seed 保留为 Best。
原始反思文本未经手工修改；可公开的指令文本见 [prompts.json](core-sprint-001/prompts.json)。

| 组 | 真实新提案 / 实际评估 / 接受的新候选 | 任务评估次数 | 实际 Train 覆盖 | Best验证均分 |
|---|---|---:|---|---:|
| Basic | 1 / 1 / 0 | 4/8 | 仅7（计划池1,6,7） | 0.5 |
| Structured | 1 / 1 / 0 | 4/8 | 仅7（计划池1,6,7） | 0.5 |

每组实际评估两个不同文本（Seed+提案）；GEPA accepted pool 仅含 Seed。并非用 Mock
或手工候选代替真实搜索，也没有把未接受的提案写为 Best。

| 顺序 | 用途 / Prompt | Basic Reward | Structured Reward |
|---|---|---:|---:|
| 1 | Val8 / Seed | 0 | 0 |
| 2 | Val10 / Seed | 1 | 1 |
| 3 | Train7 / Seed | 1 | 1 |
| 4 | Train7 / 该组新提案 | 1 | 1 |

上述8次任务均 user_stop；Val8 DB不匹配，Val10和Train7 DB匹配。完整评分分解、
Action检查和资源记录见 [results.json](core-sprint-001/results.json)。

两个提案都强化参数核对、澄清与变更确认；Structured提案额外强调一次针对性提问和
逐项确认。Basic新候选哈希 `75a246d8393fe2af3b8ae37f82b0142db7ce11295721469417e86b3339d2c9f8`；
Structured为 `67cb3986561488a14cdc9d44b474e0e487119f6c89dcb19f04ab9d6c6e9d8fa2`。
Basic提案的Train7使用6次工具，Structured提案使用7次（多一次订单查询）；
两者 Reward 同为1。工具路径不同不构成错误，新增措辞也不构成性能提升。

Basic消耗74/92请求，Structured70/92。剩余18/22均不足下一任务最多24次调用的预留，
官方停止回调因此结束搜索；不是8次评估额度全部耗尽，也没有额外提案被隐瞒。
两个被拒候选未进入新一轮完整验证；Best只依据Seed已完成的2任务验证选择。

## 3. M4-B：反馈实际增加了什么

两组从相同 Seed 独立优化，Agent/User/Reflection、任务池、随机种子、评分与预算上限相同。
唯一实验信息差别是 Structured evaluator info 增加现有 `diagnose()` 输出；
Basic含官方分数、状态、终止原因、消息数、工具名和Trace位置，不含原始自由文本/隐藏答案。

**实际反思仅采样成功的Train7。** Structured新增一条 `task_completion`，证据为
`/termination_reason=user_stop`，并明确不能由此证明业务完成。Basic本来已有该终止字段，
因此新增信息大部分重复。没有工具执行错误、参数错误或失败诊断送入这次Reflection。
Val8的结构化记录含 `uncertain_failure`，但Val8没有被采入反思样本。

| Reflection | 输入 Tokens | 输出 Tokens | 估算人民币 | finish_reason |
|---|---:|---:|---:|---|
| Basic | 439 | 126 | 0.0006032 | stop |
| Structured | 505 | 140 | 0.0006840 | stop |

输入增加66 Tokens，输出增加14；没有观察到额外收益。不能从这一次成功样本推断
Structured对所有失败都无效，更不能宣称它优于Basic。诊断未覆盖Simulator偏离、
业务偏好理解、认证遗漏、无依据承诺等问题；本轮没有临时增加分类器、规则或Judge。

## 4. M5：冻结后的完整独立 Test

冻结三组 Best 哈希均为
`bf472daae29fe741f5ce5ae0543946e3a640493134612a00dd9cc4e8be10c870`。
按Task5→9→12，每任务Baseline→Basic→Structured，各1 Trial。看到Test后没有调Prompt、
重选Best、继续搜索、追加Trial或重试。所有Test内容/隐藏状态从未传给GEPA。

| Task | 组 | 官方Reward | 终止 | DB match | Action匹配数 | 请求 | 输入/输出Tokens | 估算¥ |
|---|---|---:|---|---|---|---:|---:|---:|
| 5 | Baseline | 1 | user_stop | true | 5/5 | 23 | 126187 / 2521 | 0.1059916 |
| 5 | Basic | 0 | max_steps | unavailable | unavailable | 24 | 134084 / 2152 | 0.1115712 |
| 5 | Structured | 1 | user_stop | true | 5/5 | 24 | 126430 / 2194 | 0.1055320 |
| 9 | Baseline | 1 | user_stop | true | 6/6 | 22 | 112824 / 2372 | 0.0950032 |
| 9 | Basic | 0 | max_steps | unavailable | unavailable | 24 | 132696 / 2346 | 0.1108488 |
| 9 | Structured | 0 | max_steps | unavailable | unavailable | 23 | 137908 / 2320 | 0.1149664 |
| 12 | Baseline | 1 | user_stop | true | 1/5 | 4 | 11058 / 223 | 0.0092924 |
| 12 | Basic | 1 | user_stop | true | 4/5 | 11 | 44169 / 1319 | 0.0379732 |
| 12 | Structured | 1 | user_stop | true | 2/5 | 7 | 22905 / 565 | 0.0194540 |

完整成功数/分母：Baseline **3/3**，Basic **1/3**，Structured **2/3**；平均官方Reward
分别 **1.000 / 0.333 / 0.667**。Not run=0、基础设施故障=0、Step截断=3。
三组Prompt相同，以上是同一Prompt的独立重复，**不是三个不同策略的有效性能优劣证明**。
固定seed/temperature0并未保证托管Agent和Simulator完全确定；固定执行顺序、单Trial、
相似任务内容和小样本也限制了因果解释。没有统计显著性主张。

正常终止任务的官方 reward_basis 为 DB + NL_ASSERTION；NL assertions为空，
对应分量为中性1，没有付费Judge。Action检查作为官方详情保存，但不擅自加入主Reward。
Step截断时上游直接给官方0，DB/Action/NL明细未执行而为 unavailable；不填造DB失败。
工具错误数为0，模型返回没有 `finish_reason=length`，这不等于业务或Policy全部正确。

## 5. 人工 Trace 审查：成功与失败都保留

- **正常终止的业务失败，Val8**：两组Seed均DB不匹配、exchange动作不匹配。
  Basic轨迹中初始用户要求更亮的灯，后续Simulator却接受低亮度电池灯；本地官方动作
  检查期望另一亮度/电源选项。可观察到偏好漂移与状态差异，但不能将全部责任归给Agent，
  也不能只凭Reward=0得出原因。M4准确返回“不确定”，没有虚构参数/工具异常。
- **工具已执行但未正常结束，Test5 Basic**：已请求退水瓶，最后Agent说明完成，
  尚未得到用户STOP即达到32 Steps。Test9 Basic/Structured也已请求换灯，最后用户感谢
  后Agent继续客套，仍无STOP而截断。原始官方0全部计入三任务分母；不以DB操作成功改为1。
  Step计数是官方orchestrator循环，包含用户/工具交互；导出列表还含初始消息，不能把
  消息条数等同于模型请求数或Steps。详细Trace位置见JSON的path字段。
- **官方满分仍存在Policy问题，Test12 Baseline**：用户要求人工服务后Agent直接调用
  transfer，没有先认证。固定Retail Policy要求对话开始定位用户身份；人工审查据此
  标注遗漏。该任务官方Reward仍为1，Action只匹配1/5，未改分或新建付费Judge。
  不把每个未匹配read动作都当成必经步骤，只针对明确政策文本及实际行为作判断。
- **无依据的承诺，Test5 Baseline**：`/messages/30` 给出退货后数个工作日到账的说法，
  而工具只确认return_requested，对应退货政策未给这一时效。将其列为人工审查的
  无依据时效承诺，不能用官方Reward=1宣称整段回复已被验证。完整客户字段不公开。
- **成功案例**：Test5 Baseline最终按用户改变后的意图退水瓶且不换灯，正常STOP、
  DB和官方Action匹配；Test9 Baseline只换灯、不动水瓶，正常STOP且官方匹配。

现有M4只报告显式工具错误、参数绑定异常、结束状态和未知失败。它没有Policy验证器，
也不会发现上述全部语义问题。这是这版算法的实际能力边界，非已解决的失败分类。

## 6. 共享预算、实际 Usage 与费用

| 阶段 | 请求 / 阶段上限 | 输入Tokens | 输出Tokens | 估算¥ |
|---|---:|---:|---:|---:|
| Basic（含Reflection） | 74/92 | 363051 | 7305 | 0.3050508 |
| Structured（含Reflection） | 70/92 | 329728 | 6893 | 0.2775684 |
| Test | 162/216 | 848261 | 16012 | 0.7106328 |
| 总计 | 306/400 | 1541040 | 30210 | **1.2932520** |

| 角色 | 请求 | 输入Tokens | 输出Tokens | 估算¥ |
|---|---:|---:|---:|---:|
| Agent | 196 | 1412448 | 26311 | 1.1825804 |
| Simulator | 108 | 127648 | 3633 | 0.1093844 |
| Reflection | 2 | 944 | 266 | 0.0012872 |

总Tokens **1,571,250**。306条发送前admitted、306条returned、306个唯一响应ID，
304个任务响应+2个反思响应逐一核对；Usage缺失=0、异常=0、pending=null、stopped=null。
没有Task0真实调用、并发或自动任务重试。首末请求UTC09:50:23–10:11:55（北京时间
17:50:23–18:11:55），跨度1292秒；累计请求等待约816秒，其余包括独立进程/环境初始化。
每次任务时长与请求时延保留在JSON，不能把串行启动开销当作模型推理时间。

所有请求输入均≤12365 Tokens，适用冻结的北京非思考≤128k价格：输入¥0.8/百万、
输出¥2/百万。[阿里云官方价格](https://help.aliyun.com/zh/model-studio/qwen-plus)
于2026-11-01复核；未扣缓存/免费额度/促销。**实际账单不可获得**；¥30是应用估算
停止阈值，云端不保证硬封顶，一次在途请求可能跨过阈值。GEPA元数据中的adapter_cost=0
仅表示未接GEPA内部计费，不表示免费，以共享账本为准。

历史两次Task0烟测另计18请求、估算¥0.0839208，不占本轮授权预算。
两次记录的18/21个原始文件哈希逐一验证未变；第一次raw Reward0依旧保留。

## 7. 复现、公开产物与验收

实际执行命令（一次，退出0）：
```powershell
environments/gepa/.venv/Scripts/python.exe -m agent_evolve.experiment --config examples/core_experiment.json --live
```

该run_id已经使用，禁止覆盖；不得为再次付费运行自行换ID绕过本轮已结束的授权。
未来复现实验需要新审查的预算/ID。默认不带`--live`仅验证配置、零模型请求。
安装/固定源码见 [runbook](../CORE_EXPERIMENT_RUNBOOK.md) 与已有M2/M3环境说明。

- 私有完整记录：`runs/core/core-sprint-001/`，含预算事件、848个文件、原始反思、
  每任务配置/Prompt/Trace/RewardInfo/最终状态和调用日志；全部保持Git忽略。
- 公开：经审查的 [标量与诊断](core-sprint-001/results.json)、
  [实际候选文本](core-sprint-001/prompts.json)、[116项产物哈希](core-sprint-001/manifest.json)
  与环境快照。无客户完整信息、凭据CSV、原始鉴权字段或完整对话/反思日志。
- 离线检查及实际命令见 [validation](../validation/CORE_SPRINT_VALIDATION.md)。
  真实模型结果与合成测试成绩严格区分；测试不替代正式效果证据。
- M3验收：新候选确实由真实Reflection产生并被真实评分，完成。
  M4验收：同条件独立Basic/Structured比较与反馈局限，完成。
  M5实验：9/9最终试验、成本、失败与人工审查，完成；GitHub交付独立分支/PR待审查，
  不合并main、不发布Release。

下一步最有价值的是审查“反思只看到成功样本”与终止/Simulator波动如何影响可用反馈，
再另行设计一个有明确失败证据、仍隔离Test的小预算实验。本轮不继续搜索或追加任务。
