"""Validate plugin.json, .mcp.json, and the marketplace entry for ppc-manager."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
MCP_JSON = PLUGIN_ROOT / ".mcp.json"
MARKETPLACE_JSON = PLUGIN_ROOT.parent.parent / ".claude-plugin" / "marketplace.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestPluginJson:
    def test_exists(self):
        assert PLUGIN_JSON.exists()

    def test_required_fields(self):
        data = _load(PLUGIN_JSON)
        for field in (
            "name",
            "version",
            "description",
            "author",
            "license",
            "keywords",
            "skills",
            "userConfig",
        ):
            assert field in data, f"plugin.json missing field: {field}"

    def test_name_is_kebab(self):
        data = _load(PLUGIN_JSON)
        assert data["name"] == "ppc-manager"

    def test_user_config_has_passphrase(self):
        data = _load(PLUGIN_JSON)
        uc = data["userConfig"]
        assert "ppc_vault_passphrase" in uc
        assert uc["ppc_vault_passphrase"]["sensitive"] is True

    def test_sensitive_fields_match_plan(self):
        data = _load(PLUGIN_JSON)
        uc = data["userConfig"]
        sensitive = {k for k, v in uc.items() if v.get("sensitive")}
        assert "ppc_vault_passphrase" in sensitive
        assert "google_ads_developer_token" in sensitive
        assert "meta_app_secret" in sensitive
        # non-sensitive values
        assert uc["meta_app_id"]["sensitive"] is False
        assert uc["google_ads_login_customer_id"]["sensitive"] is False


class TestMcpJson:
    def test_exists(self):
        assert MCP_JSON.exists()

    def test_is_valid_json(self):
        data = _load(MCP_JSON)
        assert "mcpServers" in data


class TestMarketplaceEntry:
    def test_marketplace_exists(self):
        assert MARKETPLACE_JSON.exists()

    def test_ppc_manager_is_registered(self):
        data = _load(MARKETPLACE_JSON)
        names = [p["name"] for p in data.get("plugins", [])]
        assert "ppc-manager" in names, (
            f"ppc-manager not registered in marketplace.json. Found: {names}"
        )

    def test_ppc_manager_fields(self):
        data = _load(MARKETPLACE_JSON)
        entries = [p for p in data["plugins"] if p["name"] == "ppc-manager"]
        assert entries, "ppc-manager entry missing from marketplace.json"
        entry = entries[0]
        assert "version" in entry
        assert "description" in entry
        assert "source" in entry
        assert entry["source"] == "ppc-manager"
