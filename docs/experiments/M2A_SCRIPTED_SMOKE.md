# M2-A official-framework scripted smoke — no model

- Run ID: `tau-scripted-evidence-004`; status: executed, **mock**.
- Question: can official Retail tools, orchestration and ALL scoring produce a
  serializable, attributable trace without any model invocation?
- Timestamp: 2026-11-01T04:54:59.066008Z (12:54:59 Asia/Shanghai).
- Project baseline: afb0e8eb2f6721a67969e4d5511490393949f31a + dirty M2-A working tree;
  exact tested project source hashes: `../validation/M2A_SOURCE_MANIFEST.json`.
- Command: `environments/tau/.venv/Scripts/python.exe -m agent_evolve.baseline
  --config .cache/m2-tau_mock-004.json` (native Windows permissions, socket/DNS denial
  inside runner; effective config is saved under run directory).
- Config SHA256: `3cf0078f218376220b84a4204c23608b6d102addaa908cd62d9dcc47a2756b69`.
- Upstream tau2 2.0.0 SHA: `da0835f6c67baef58bdda18f2a3b037dfb3a1754`.
- Retail task 0, official train split; task content SHA256:
  `4586aad9ec3c2d84f5a063ad6cff0a1856a0f5b808f6f44b22a7cc61e21b6227`.
- One trial (0), seed 42, max_steps 12. Scripted participants are deterministic;
  this says nothing about hosted-model seed reproducibility.
- Instruction hash: `bf472daae29fe741f5ce5ae0543946e3a640493134612a00dd9cc4e8be10c870`;
  fixed Policy/system hashes and text in run `prompt.json`; Retail data identity
  in run metadata and committed source manifest. No Policy/task/scoring change.
- Windows AMD64 / Python 3.12.8; tau2 2.0.0 / LiteLLM 1.82.6; all transitive versions
  in `environments/tau/uv.lock`. No GPU needed, no provider/model configured to execute.
- Actual participants: scripted Agent asks `get_order_details` for #W2378156,
  actual official tool returns the order, Agent ends and scripted User stops.
  No reference/gold action replay as the Agent's solution.
- Official Reward: **0.0**, DB check false; NL assertion list empty (neutral component).
  Status: normal `user_stop` → task_failure for the script. No task success claim.
- Simulation loop duration: **0.004540200003248174 s**; CLI wall time **25.656 s**
  includes imports/environment loading/evaluation/cleanup. These are not model latency.
- Model calls: 0. Token usage / provider bill / message cost estimates: **unavailable**.
  No claimed observed currency cost metric. No custom diagnostic metric.
- Local artifacts: `runs/m2/tau-scripted-evidence-004/` (ignored, never overwritten).
  Portable actual excerpt: `../validation/M2A_MOCK_EXAMPLE.json`; original normalized
  result SHA256 `c2a9d531be4e3140f86a7ab60904f7d0b7e9668724337259947f547a9effa7bf`.
- Data are public official benchmark records; no private user-supplied data or model keys.

Supported conclusion: official tool/trace/reward export works on this scripted path.
Unsupported: real Agent baseline, provider compatibility, task-solving performance,
Prompt improvement, generalization or cost control. Separate tests check repeated
task 0, different task 1, DB/history isolation and injected faults. Next step is
review of the Live proposal only; no M2-B or GEPA executed.
