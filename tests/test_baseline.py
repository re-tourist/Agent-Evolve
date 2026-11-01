import json
import socket
import subprocess
import sys
from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path

import pytest

from agent_evolve.baseline import (
    Config,
    FixtureBackend,
    LiveNotApprovedError,
    Prompt,
    SimulatorError,
    deny_network,
    digest,
    execute,
    normalize,
)


@pytest.fixture
def config(tmp_path):
    return Config(
        mode="mock",
        backend="fixture",
        task_ids=("fixture-retail-001",),
        instruction="Be careful.",
        output_dir=str(tmp_path),
        run_id="test",
    )


def test_policy_is_separate_and_frozen():
    first = Prompt("A", "FIXED official policy\n")
    second = Prompt("B", first.policy)
    assert first.record()["policy_sha256"] == second.record()["policy_sha256"]
    assert first.record()["system_sha256"] != second.record()["system_sha256"]
    assert first.system.endswith("<policy>\nFIXED official policy\n\n</policy>")
    with pytest.raises(FrozenInstanceError):
        first.policy = "changed"


@pytest.mark.parametrize(
    "override",
    [
        {"mode": "invalid"},
        {"domain": "airline"},
        {"num_tasks": 0},
        {"num_tasks": True},
        {"num_tasks": 2},
        {"seed": -1},
        {"seed": 1.1},
        {"max_steps": 1000},
        {"task_ids": ("x", "x")},
        {"task_ids": ()},
        {"task_ids": ("../x",)},
        {"task_ids": "x"},
        {"run_id": "../escape"},
        {"instruction": " "},
        {"agent_args": {"api_key": "secret"}},
        {"user_args": []},
        {"agent_args": {"max_tokens": 1.1}},
        {"agent_args": {"temperature": float("nan")}},
        {"user_args": {"num_retries": 1}},
        {"agent_model": "https://key@example.com"},
    ],
)
def test_invalid_config(config, override):
    with pytest.raises((ValueError, TypeError)):
        replace(config, **override)


def test_config_file_relative_prompt_and_unknown_fields(config, tmp_path):
    content = asdict(config)
    del content["instruction"]
    content.update(instruction_file="prompt.txt", output_dir="out")
    (tmp_path / "prompt.txt").write_text("Prompt from file", encoding="utf-8")
    filename = tmp_path / "config.json"
    filename.write_text(json.dumps(content), encoding="utf-8")
    loaded = Config.load(filename)
    assert loaded.instruction == "Prompt from file"
    assert loaded.output_dir == str(tmp_path / "out")
    content["policy"] = "cannot override"
    filename.write_text(json.dumps(content), encoding="utf-8")
    with pytest.raises(TypeError):
        Config.load(filename)


def test_artifacts_trace_and_no_overwrite(config):
    directory = execute(config)
    original = (directory / "prompt.json").read_bytes()
    result = json.loads((directory / "fixture-retail-001.json").read_text())
    metadata = json.loads((directory / "metadata.json").read_text())
    assert result["official_task_reward"] is None  # synthetic fixture is not official scoring
    assert result["reward_availability"] == "unavailable"
    assert result["excluded_from_task_metrics"]
    assert result["messages"][1]["tool_calls"][0]["arguments"] == {"order_id": "fixture-retail-001"}
    assert result["messages"][2]["content"] == {"status": "pending"}
    assert metadata["model_calls"] == 0
    assert metadata["prompt_sha256"] == digest(config.instruction)
    with pytest.raises(FileExistsError):
        execute(config)
    assert (directory / "prompt.json").read_bytes() == original


def test_repeated_and_different_fixture_tasks_are_fresh(config):
    backend = FixtureBackend()
    first = execute(config, backend=backend)
    second_config = replace(
        config, run_id="repeat", task_ids=("fixture-retail-001", "fixture-retail-002"), num_tasks=2
    )
    second = execute(second_config, backend=backend)
    messages = []
    for directory, name in [
        (first, "fixture-retail-001"),
        (second, "fixture-retail-001"),
        (second, "fixture-retail-002"),
    ]:
        trace = json.loads((directory / f"{name}.json").read_text())["messages"]
        assert len(trace) == 4
        assert trace[2]["content"]["status"] == "pending"
        messages.append(trace)
    assert messages[0] == messages[1]


def test_unknown_task_before_directory_creation(config):
    with pytest.raises(ValueError, match="Unknown fixture"):
        execute(replace(config, task_ids=("unknown",)))
    assert not (Path(config.output_dir) / config.run_id).exists()


def test_offline_never_executes_participants(config):
    class Backend(FixtureBackend):
        def run(self, *args):
            raise AssertionError("Must not run")

    directory = execute(replace(config, mode="offline"), backend=Backend())
    result = json.loads((directory / "fixture-retail-001.json").read_text())
    assert result["status"] == "preflight_only"
    assert result["messages"] == []


def test_live_rejected_before_import_backend_or_output(config, monkeypatch):
    monkeypatch.setenv("AGENT_EVOLVE_LIVE_APPROVED", "true")
    with pytest.raises(LiveNotApprovedError):
        execute(replace(config, mode="live", backend="tau"), backend=object())
    assert not (Path(config.output_dir) / config.run_id).exists()


def test_network_denied():
    with deny_network(), pytest.raises(PermissionError):
        socket.create_connection(("example.com", 443))


@pytest.mark.parametrize(
    ("reason", "status", "reward"),
    [
        ("user_stop", "task_success", 1.0),
        ("agent_stop", "task_failure", 0.0),
        ("infrastructure_error", "infrastructure_error", None),
        ("timeout", "infrastructure_error", None),
        ("user_error", "simulator_error", None),
        ("agent_error", "agent_protocol_error", None),
    ],
)
def test_reward_and_error_semantics(reason, status, reward):
    raw = {
        "termination_reason": reason,
        "reward_info": {
            "reward": 1.0 if reward else 0.0,
            "db_check": {"db_match": False},
            "reward_breakdown": {"DB": 0.0},
        },
        "messages": [],
    }
    result = normalize(raw)
    assert result["status"] == status
    assert result["official_task_reward"] == reward
    assert result["evaluation_details"] == raw["reward_info"]
    assert result["excluded_from_task_metrics"] == (reward is None)


@pytest.mark.parametrize(
    "error", [ConnectionError("secret"), SimulatorError("secret"), RuntimeError("secret")]
)
def test_exception_export_never_zero_scores_or_leaks_message(config, error):
    class Backend(FixtureBackend):
        def run(self, *args):
            raise error

    directory = execute(config, backend=Backend())
    result = json.loads((directory / "fixture-retail-001.json").read_text())
    assert result["official_task_reward"] is None
    assert result["excluded_from_task_metrics"]
    assert "secret" not in result["error"]["message"].replace("secrets", "")
    expected = (
        "simulator_error"
        if isinstance(error, SimulatorError)
        else ("infrastructure_error" if isinstance(error, OSError) else "runner_error")
    )
    assert result["status"] == expected


def test_cli_live_refusal(config, tmp_path):
    filename = tmp_path / "live.json"
    filename.write_text(json.dumps(asdict(replace(config, mode="live"))), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "agent_evolve.baseline", "--config", str(filename)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 2
    assert "M2-A: live disabled" in result.stderr


def test_missing_cost_is_unavailable_not_upstream_default_zero():
    raw = {
        "agent_cost": 0.0,
        "user_cost": 0.0,
        "messages": [{"role": "assistant", "cost": None}, {"role": "user"}],
    }
    assert normalize(raw)["provider_cost"] == {"agent": None, "user": None}
    raw["messages"] = [{"role": "assistant", "cost": 0.01}, {"role": "assistant", "cost": 0.02}]
    assert normalize(raw)["provider_cost"] == {"agent": 0.03, "user": None}
