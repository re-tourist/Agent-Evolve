"""Verify installed package metadata without importing model SDKs."""

from importlib.metadata import metadata, version

import agent_evolve


def test_installed_package_metadata():
    assert version("agent-evolve") == agent_evolve.__version__
    assert set(metadata("agent-evolve")["Requires-Python"].split(",")) == {">=3.12", "<3.13"}
