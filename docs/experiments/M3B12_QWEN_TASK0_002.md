# M3-B1.2：正常任务终止验证

**qwen-task0-002 已正常终止，官方 Reward=1.0。仅执行本轮获批的一次任务；
无重试、无第三次任务、无 GEPA，现已停止。**

## 与第一次的差异
| 项目 | qwen-task0-001 | qwen-task0-002 |
|---|---|---|
| max_steps 配置 | 12 | 32 |
| 单请求输出上限 | 512 | 1024 Tokens |
| 调用准入期限 | 180s | 600s；启动器进程总期限 600s（含导入） |
| 共享调用 / 请求超时 / 重试 | 24 / 30s / 0 | 不变，串行 |
| 正常结束 | 否，max_steps | **是，user_stop** |
| 原始官方 Reward | **0.0** | **1.0** |
| 归一化工程分数 | null，step_limit | 1.0，task_success |
| 模型调用 | 8 | 10，全数返回 |
| finish_reason=length | messages[10] 一次 | **0 次** |
| 输入 / 输出 Tokens | 42,210 / 1,717 | 53,736 / 1,865 |
| Usage 估算费用 | ¥0.037202 | **¥0.0467188，约 ¥0.05** |

模型、Task 0、Trial=1、seed=42、Agent Instruction、System Prompt/Policy 和工具未改。
两次的 task.json 与 prompt.json 字节完全相同；官方源码/评分未修改。
这不是 Prompt 优化效果比较，也不据单次成功推导泛化能力。

第一次实际日志为 Step 0–12，共 13 个参与者/环境流转。官方在等待环境结果时
跳过上限检查，因此最后的换货工具响应得以完成，随后 max_steps 阻止下一轮收尾。
第一次 messages[10] 被截断的是自然语言说明（尾部为未完的订单说明），该事件没有
tool_calls，未观察到工具参数截断。本次日志 Step 0–14，共 15 次流转、16 条消息，
未接近新的 32 Steps 上限。Steps 不等于模型调用次数。

第一次运行属于**人为设置的步骤上限截断**，原始 Reward=0 永久保留。
其所有 18 个产物哈希均未变。旧 null/excluded 仅描述 smoke 工程状态；正式 Benchmark
若纳入该次试验，必须保留官方 0 和尝试分母，不能排除它来抬高成功率。
本次在 0.json/summary.json 额外明确导出 official_raw_reward，并更新实验协议；
没有改写旧产物或 baseline.normalize，没有执行正式 Benchmark 汇总。

## 官方评分、业务状态与交互
- 终止：user_stop，子进程 exit=0；官方与归一化 Reward 均 1.0，excluded=false。
- 官方 DB 检查：db_match=true、db_reward=1.0。
- Reward breakdown：DB=1.0、NL_ASSERTION=1.0。Task 0 的 NL 断言为空，
  NL 项为官方空断言结果，不代表调用了 Judge 或证明开放式承诺都正确。
- 官方动作检查 5/5 匹配。实际工具调用为身份查询、订单查询、两次商品查询、一次换货；
  5 个响应均 executed / error=false。保持原评分，无自定义加权或手工改分。
- 实际最终环境快照 final_state.json：订单为 exchange requested；一次性登记两件
  换货商品及对应替换项，exchange_price_difference=-16.63。该快照来自运行后的实际
  Orchestrator 环境，未导出全库或隐藏目标，亦不替代官方 DB 评分。
- 完整交互：用户提出两件商品的换货需求 → Agent 认证身份并查询 → 说明可用选项及
  差价 → 用户确认两件商品及退款方式 → Agent 调用换货工具 → 确认处理结果并收尾 →
  User Simulator 发送 ###STOP###。完整正文/工具参数/响应保存在原始 Trace，报告不复制
  客户地址或支付字段。

## 请求、费用、M4 与剩余问题
Agent 7 次：输入 50,344 / 输出 1,516；User Simulator 3 次：输入 3,392 / 输出 349。
合计 **55,601 Tokens**。逐调用日志与消息 usage 汇总一致，10 个 Provider response ID
互异，返回模型均 qwen-plus-2025-12-01。无接口错误，无 Token 截断。

按当日[百炼北京模型价格](https://help.aliyun.com/zh/model-studio/qwen-plus)，最大单次输入
9,904，适用 <=128K 非思考档：输入 ¥0.8/M、输出 ¥2/M；不计缓存/赠送优惠估算：
`53736×0.8/1e6 + 1865×2/1e6 = ¥0.0467188`。**实际扣费未知，以平台账单为准**；
¥1 只是预算参考，没有假称硬性费用控制。两次累计估算 ¥0.0839208，分开保留各次记录。
本次墙钟 70.500s、simulation duration 46.637s；180s 并未影响第一次，但可能影响更长
轨迹，因此本次经批准提高到 600s。外层超时杀进程不保证取消供应商已在途计费。

M4 输出只有 task_completion / certain=true，证据 /termination_reason=user_stop。
无工具错误、参数错误、uncertain_failure。它确认观察到停止，业务成功结论仍来自
官方 Reward/DB 检查，不靠诊断模块推断。

剩余语义风险：messages[12]/[14] 出现“预付标签、退货授权号、15 分钟内邮件”等承诺，
未在固定 Policy 或本次工具返回中找到相应依据。这里仅记录人工证据核对，不擅自修改
官方 Reward，也不把这些承诺归入 M4-A 尚未实现的语义诊断。Reward=1 不覆盖这些未检验维度。

## 执行与验证证据
初始源码 d17e435；独立分支 codex/m3b1-2-normal-termination。用户本轮明确授权后执行。
实际命令 `environments/tau/.venv/Scripts/python.exe .cache/qwen_b12_once.py`，私有启动器
沿用安全 CSV 加载器，临时子进程环境注入 Key 和同一北京业务空间端点，再调用原
qwen_smoke.main（--live --approve-single-task --run-id qwen-task0-002）。独占标记禁止重启，
subprocess timeout=600，Key 不在命令行；原 CSV 字节不变且持续未跟踪/已忽略。

离线验证（均 exit=0）：
- `uv run --offline --frozen python -m pytest tests/test_qwen_smoke.py -q --basetemp=.cache/pytest-qwen002-guards`：4 passed，0.17s。
- `AGENT_EVOLVE_TAU_TESTS=1 environments/tau/.venv/Scripts/python.exe -m pytest tests/integration/test_qwen_transport.py -q --tb=short --basetemp=.cache/pytest-qwen002-offline`：3 passed，26.66s；3 条已知上游 Windows/deprecation 警告保留。
- Ruff check / format：本次三个 Python 文件通过。只修正一条过长说明字符串，未弱化测试。
- 原始任务/Prompt/Policy/工具及上游源码保持原样；原始官方评分与工程标记分开保存。

产物：[runs/qwen/qwen-task0-002](../../runs/qwen/qwen-task0-002/)，含原始完整交互、配置、
官方 RewardInfo、元数据/逐调用日志、最终状态、M4 输出及分析。
[可审查摘要及双运行哈希](../validation/M3B12_QWEN_EVIDENCE.json) 不含密钥。
最终安全复核：第一次 18 个产物、第二次 21 个产物及 5 个源文件哈希全部匹配；
仓库/运行目录/暂存区精确密钥命中均为 0，CSV 继续忽略且未改动。仅做本地提交，不推送。

**后续判断：单任务正常终止与官方业务评分的前置关卡已满足，可进入 M3-B2 方案审查。
真实 Reflection 接入、多角色预算与最小任务集仍需单独审查授权；本轮不实现或执行它们。**
