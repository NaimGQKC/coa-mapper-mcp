"""Tests for the MCP server tool functions.

The server module calls ``FastMCP(description=...)`` at import time, which
may be incompatible with the installed fastmcp version. We mock FastMCP
before importing the server so that the module loads cleanly, then patch
the module-level ``mapper`` with one that reads from our temp sample data.
"""

from __future__ import annotations

import json
import sys
import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from coa_mapper_mcp.mapper import CoaMapper


def _make_fake_fastmcp():
    """Return a fake FastMCP class whose .tool() is a no-op decorator."""
    class FakeMCP:
        def __init__(self, *args, **kwargs):
            pass
        def tool(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
        def run(self):
            pass
    return FakeMCP


@pytest.fixture()
def patched_server(tmp_data_dir: Path, monkeypatch: pytest.MonkeyPatch):
    """Import the server module with a mocked FastMCP and temp-data mapper."""
    import coa_mapper_mcp.mapper as mapper_mod
    monkeypatch.setattr(mapper_mod, "DATA_DIR", tmp_data_dir)

    test_mapper = CoaMapper()

    # Ensure server module is not cached
    mod_key = "coa_mapper_mcp.server"
    saved = sys.modules.pop(mod_key, None)

    # Patch FastMCP so the import doesn't fail on the description kwarg
    fake_mcp_class = _make_fake_fastmcp()
    monkeypatch.setattr("fastmcp.FastMCP", fake_mcp_class)

    import coa_mapper_mcp.server as server_mod
    importlib.reload(server_mod)

    monkeypatch.setattr(server_mod, "mapper", test_mapper)
    yield server_mod

    # Restore original cached module if any
    if saved is not None:
        sys.modules[mod_key] = saved
    else:
        sys.modules.pop(mod_key, None)


def test_suggest_mapping_tool_returns_json(patched_server):
    """suggest_mapping tool should return valid JSON with expected keys."""
    raw = patched_server.suggest_mapping("Cash", "quickbooks", "xero")
    data = json.loads(raw)

    assert isinstance(data, list)
    assert len(data) >= 1
    first = data[0]
    assert "source" in first
    assert "target" in first
    assert "confidence" in first
    assert "reason" in first


def test_list_accounts_tool_returns_json(patched_server):
    """list_accounts tool should return valid JSON array of accounts."""
    raw = patched_server.list_accounts("quickbooks")
    data = json.loads(raw)

    assert isinstance(data, list)
    assert len(data) == 10
    for acct in data:
        assert "code" in acct
        assert "name" in acct
        assert "type" in acct


def test_invalid_platform_graceful_error(patched_server):
    """Requesting accounts for an unknown platform should return an empty list, not crash."""
    raw = patched_server.list_accounts("not_a_platform")
    data = json.loads(raw)
    assert data == []
