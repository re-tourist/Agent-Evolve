import json

import pytest

from agent_evolve.baseline import LiveNotApprovedError, ProviderError
from agent_evolve.qwen_smoke import MODEL, CallLimit, Calls, run


def test_live_requires_opt_in_before_import_or_credentials():
    with pytest.raises(LiveNotApprovedError):
        run("gate", live=True)


def test_call_forwarding_limit_and_secret_free_logs(tmp_path):
    seen = []

    def fake(**kwargs):
        seen.append(kwargs)
        return {"usage": {"prompt_tokens": 10, "completion_tokens": 3}}

    calls = Calls(fake, "SECRET_SENTINEL", tmp_path, limit=1)
    calls(model=MODEL, messages=[], tools=[{"type": "function"}])
    assert seen[0]["extra_body"] == {"enable_thinking": False}
    assert seen[0]["api_key"] == "SECRET_SENTINEL"
    assert seen[0]["num_retries"] == seen[0]["max_retries"] == 0
    assert seen[0]["timeout"] == 30 and seen[0]["max_tokens"] == 512
    with pytest.raises(CallLimit):
        calls(model=MODEL)
    assert "SECRET_SENTINEL" not in (tmp_path / "call-001.json").read_text()
    assert json.loads((tmp_path / "call-001.json").read_text())["status"] == "returned"


def test_provider_fault_stops_subsequent_calls(tmp_path):
    def failed(**kwargs):
        raise RuntimeError("SECRET_SENTINEL")

    calls = Calls(failed, "secret", tmp_path)
    with pytest.raises(ProviderError, match="withheld"):
        calls(model=MODEL)
    with pytest.raises(CallLimit):
        calls(model=MODEL)
    assert calls.count == 1
    assert "SECRET_SENTINEL" not in (tmp_path / "call-001.json").read_text()


def test_time_and_unknown_provider_refused(tmp_path):
    calls = Calls(lambda **kwargs: pytest.fail("No transport"), "secret", tmp_path, seconds=-1)
    with pytest.raises(CallLimit):
        calls(model=MODEL)
    calls = Calls(lambda **kwargs: pytest.fail("No transport"), "secret", tmp_path)
    with pytest.raises(ProviderError):
        calls(model="openai/unexpected-judge")
    assert calls.count == 0
