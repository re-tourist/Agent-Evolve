# M3-B1 首次真实 Qwen 单任务记录

Run ID：`qwen-task0-001`。用户明确授权一次；**已执行一次并停止，无重试、无第二次任务、无 GEPA**。

## 结果判断
真实 API 集成链路已验证：Agent、User Simulator 和 Tool Calling 正常交互，8 次模型调用全部返回。
任务在 **12 Steps 上限**触发 `max_steps`，未获得正常终止条件下的业务验收。
官方原始 RewardInfo 返回 **0.0**，理由为运行提前终止；项目归一化为
`status=step_limit`、`official_task_reward=null`、`excluded_from_task_metrics=true`。
这不是认证/网络/权限错误，也不能作为正常完成任务后的 Agent 业务失败样本。

最后的换货工具确实返回 `exchange requested`。这只证明工具调用和业务状态修改已发生；
不绕过官方评分，不推导“本来应该 Reward=1”，不另行重评分。

## 配置与执行证据
- 2026-11-01 07:58:15 UTC（北京时间 15:58:15）记录运行元数据。
- 项目源码 `01729ead055ec94345d5c589045622728c419c52`，运行时 dirty=true：
  增加了忽略规则与执行计划；Qwen/M4 产品代码未修改。
- τ-bench 2.0.0 / `da0835f6c67baef58bdda18f2a3b037dfb3a1754`。
- Retail Task 0，1 Trial，seed=42。Agent/User 均为 `qwen-plus-2025-12-01`，
  temperature=0，非思考，单次输出上限 512 Tokens。
- 共享调用上限 24、max_steps=12、请求超时 30s、SDK/LiteLLM 重试为 0；
  180s 调用准入期限，非全局硬性费用控制。未触发额外 Judge/Reflection。
- CSV 确认为键值行格式，识别 `apiKey`、`workspaceName`、`workspaceId` 和
  `openAiCompatible`。业务空间为默认业务空间，端点明确属于 `cn-beijing`。
  Key 与端点的实际可用性由本次成功返回验证，没有单独认证探测请求。
- CSV 当前及所有可见 Git 历史均未跟踪；`docs/ali/` 已忽略，`.env` 原已忽略。
  原始 CSV 字节在运行前后相同。密钥仅在内存和临时子进程环境中，未写入源码或报告。
- 实际启动命令：`environments/tau/.venv/Scripts/python.exe .cache/qwen_b1_once.py`。
  该私有启动器设置临时 `DASHSCOPE_API_KEY` / `DASHSCOPE_BASE_URL`，在子进程内
  将 `qwen_smoke.BASE` 设为 CSV 的北京业务空间专属兼容地址，再调用原 `main()`，
  参数为 `--live --approve-single-task --run-id qwen-task0-001`。
  这与准备入口唯一差别是采用 CSV 端点；未更换模型、地域或供应商。
  `.cache` 独占启动标记防止本会话误启动第二次。启动器不含任何密钥字面量。
- 子进程退出 **1**，符合 `step_limit` 的非零退出约定；总墙钟 66.922s，
  官方记录 simulation duration 43.716s。没有全套测试重跑。

## 实际交互及工具
用户模拟器提出键盘与温控器换货要求。Agent 查询身份、订单和两件商品的可用选项，
向用户说明方案并收到确认，随后发起换货。最后的工具响应成功返回，尚未继续到收尾轮次。

| Trace messages 索引（从 0 开始） | 调用 | 实际结果 |
|---|---|---|
| 2 → 3 | find_user_id_by_name_zip | executed，error=false |
| 4 → 5 | get_order_details | executed，error=false |
| 6 → 7 | get_product_details（键盘） | executed，error=false |
| 8 → 9 | get_product_details（温控器） | executed，error=false |
| 12 → 13 | exchange_delivered_order_items | executed，error=false；状态 exchange requested |

共 14 条 Trace 消息。官方 Steps 包括参与者/工具间的流转，不等于模型调用数；
官方机制允许已发起的环境响应完成后再终止，所以最后一个工具结果得到保留。
本报告仅描述实际调用，不拿隐藏参考动作序列评价路径正确性。

## 请求、Token 与费用
| 角色 | 返回的模型调用数 | Input Tokens | Output Tokens |
|---|---:|---:|---:|
| Agent | 6 | 40,606 | 1,330 |
| User Simulator | 2 | 1,604 | 387 |
| 总计 | **8** | **42,210** | **1,717** |

共 **43,927 Tokens**，call 日志与 Trace message usage 独立汇总一致。
8 条调用日志均 returned，0 个 Provider 错误；无自动重试或额外模型调用。
最大单次输入 8,922 Tokens，低于 128K 阶梯。

按 2026-11-01 核对的[百炼北京快照模型官方价格](https://help.aliyun.com/zh/model-studio/qwen-plus)，
非思考输入 ¥0.8/M、输出 ¥2/M，不计缓存折扣和赠送额度：
`42210×0.8/1e6 + 1717×2/1e6 = ¥0.037202`，约 **0.04 元**。
这是 Usage 推算，不是实际账单；控制台实际扣费、免费额度和缓存优惠未读取。

## M4-A 真实 Trace 诊断
使用未修改的 `diagnose(0.json)`，仅得到一项：
`task_completion / certain=true / /termination_reason=max_steps`。
含义是明确观察到异常终止，不确立 Agent 业务错误根因。
无工具执行/参数错误诊断。因为本次结果被排除出任务指标，归一化 Reward 为 null，
不产生 `uncertain_failure`，没有把运行上限故障当作 Reward=0 的有效失败样本。
真实 M4 输出保存在 `structured_feedback.json`。

## 工程发现与建议
1. **12 Steps 不足以在这条实际轨迹中完成收尾。** 限制按授权正常生效，未越权增加。
   下一次应先单独审查合适的 Step 上限，保持模型与官方评分一致，再申请新单任务预算。
   当前不启动第二次，不进入 GEPA 真实优化。
2. messages[10] 的 Provider `finish_reason=length`，输出达到 512 Tokens，说明一次
   Agent 回复被输出限制截断。观察到说明较长；本报告不认定这是 Step 截断的唯一原因。
   后续可先离线审查说明长度/输出额度；不能据此新增本次调用预算。
3. M4-A 目前不分类 Token 截断，属于既定范围限制；元数据仍保留该证据。
4. Key CSV 首先被误按表头格式校验，后在**任何真实请求之前**修正本地加载器以支持
   键值格式及官方北京专属域名。加载阶段拒绝不是一次失败的真实任务。
   修正只在忽略的本次启动器中，产品调用代码未改动。

## 文件与安全验收
完整产物在 `runs/qwen/qwen-task0-001/`（已忽略）：原始/归一化 Trace、task/config、
Prompt/Policy、Git/源/数据身份、8 份 call 日志、summary、脱敏启动输出、M4 反馈和分析。
本次运行目录全量精确密钥扫描为未命中；报告只保留观测概要，不复制客户/支付字段。
最终复核 18 个产物哈希和 4 个源码/私有启动器哈希一致；仓库、运行目录及暂存区完整
密钥命中均为 0。仅提交脱敏记录与忽略规则，不推送；最终记录分支 codex/m3b1-qwen-task0。
[可审查标量证据及产物哈希](../validation/M3B1_QWEN_EVIDENCE.json) 不含 API Key。
离线预检 exit=0/model_calls=0；调用保护测试 4 passed（0.17s）。未宣称重跑完整套件。

**结论：API/Tool 集成成功，受限任务未完成有效终止评分。下一步优先解决单任务验收条件，
而非开展 GEPA 搜索。当前已停止，等待用户与技术顾问审查。**
