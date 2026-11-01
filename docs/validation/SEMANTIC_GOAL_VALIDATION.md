# Semantic-feedback Goal validation — incomplete research acceptance

2026-11-01, Windows / Python3.12.8. Final closure checks after request755 stopped.
These are offline engineering checks, not proof of semantic correctness or improvement.
Final offline fault/acceptance fixes: commit `b3c21e5`.
The real study's source revisions are recorded per worker; final offline patches
do not retroactively validate the interrupted task or repair its missing Trace.

| Actual command | Exit | Actual output |
|---|---:|---|
| `.venv/Scripts/ruff.exe check .` | 0 | All checks passed |
| `.venv/Scripts/ruff.exe format --check .` | 0 | 28 files already formatted |
| `.venv/Scripts/python.exe -m pytest tests/test_semantic.py tests/test_sprint.py tests/test_qwen_smoke.py -q --basetemp .cache/semantic-closure-unit-final` | 0 | 24 passed,0.86s |
| `$env:AGENT_EVOLVE_GEPA_TESTS='1'; environments/gepa/.venv/Scripts/python.exe -m pytest tests/integration/test_sprint_gepa.py tests/integration/test_semantic_search.py -q --basetemp .cache/semantic-closure-engine-final` | 0 | 3 passed,0.81s |
| `$env:AGENT_EVOLVE_TAU_TESTS='1'; environments/tau/.venv/Scripts/python.exe -m pytest tests/integration/test_sprint_transport.py -q --basetemp .cache/semantic-closure-wire-final` | 0 | 5 passed,24.78s |
| `.venv/Scripts/python.exe -X utf8 .cache/check_semantic_delivery.py` | 0 | 200 current artifact hashes verified;119 historical sprint hashes unchanged;42 scored trials+1 unscored infrastructure attempt;ledger stopped |
| `.venv/Scripts/python.exe -X utf8 .cache/scan_public.py` | 0 | No exact-key or credential-pattern hits in current public files/outgoing Git blobs;credential CSV untracked and ignored |
| `.venv/Scripts/python.exe -X utf8 .cache/add_public_semantic_examples.py` | 0 | Published2 redacted development excerpts;original18/21 recorded smoke hashes unchanged |

The GEPA checks execute the actual pinned engine with synthetic deterministic
evaluation/reflection. The transport checks use the actual SDK and official τ
framework with local substitutes/network denial: zero paid calls. The last test
checks a Provider exception leaves a partial trajectory, no invented official
zero, a stopped ledger and a nonzero worker outcome. It does not prove how the
earlier lost partial trajectory would have looked.

Warnings: all three pytest invocations reported an existing Windows pytest-cache
write restriction; the τ invocation also reported3 upstream deprecations
(`audioop` and LiteLLM event-loop handling). They exited0. No whole-suite rerun
was used locally; normal CI runs root lint/tests and the pinned offline GEPA job.

## Evidence accounting and research status

- 755 attempted requests =753 with Usage +2 errors with unavailable Usage;
  no requests after the terminal InternalServerError, pending=null.
- Known Tokens4,098,392; known-return cost estimateRMB3.3939484; unknown-cost
  reservesRMB9.796608. Ledger totalRMB13.1905564 includes reserves, not an invoice.
- 20 baseline tasks:9 successes/11 raw official zeros. Basic23 attempts:
  22 scored+1 infrastructure fault,3 real proposals,0 accepted new candidates;
  the last complete Seed Validation checkpoint is0.8, not a final study result.
- Real gateA unproven; gateB unexecuted; gateC partial. Structured and all new
  held-out Test trials Not run. No Basic/Structured comparison or improvement claim.
- Literal citations and same-model second-pass review did not prevent several
  false causal claims. The final gate requires inspectable semantic review of an
  actual failure and the original feedback→Reflection→different-candidate→score
  artifacts. A boolean summary is insufficient; no accepted case file is forged.
- Public evidence is reviewed scalar data, original candidate instructions,
  redacted diagnostic excerpts and hashes. Full Trace/reflection/CSV stay ignored.
  Credential source hash remained unchanged; no main merge or Release.

See [the actual partial report](../experiments/SEMANTIC_STUDY_REPORT.md) and
[public evidence](../experiments/semantic-study-002/results.json). GitHub CI status
is recorded on PR21 for the final source revision; a green CI cannot accept A/B/C.
