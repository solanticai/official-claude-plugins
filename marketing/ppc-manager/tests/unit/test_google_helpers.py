"""Unit tests for scripts/lib/google_helpers.py."""

from __future__ import annotations

import json

import pytest

from lib.google_helpers import (
    ClientSecretError,
    extract_client_id_secret,
    load_client_secret,
    scopes_missing,
)
from lib.ppc_auth import GOOGLE_SCOPES_ALL


class TestLoadClientSecret:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ClientSecretError):
            load_client_secret(tmp_path / "nope.json")

    def test_invalid_json_raises(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{not valid")
        with pytest.raises(ClientSecretError):
            load_client_secret(path)

    def test_missing_installed_section_raises(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"wrong": "shape"}))
        with pytest.raises(ClientSecretError):
            load_client_secret(path)

    def test_happy_path_installed(self, fake_client_secret_file):
        data = load_client_secret(fake_client_secret_file)
        assert "installed" in data
        assert data["installed"]["client_id"].startswith("123")

    def test_happy_path_web(self, tmp_path):
        path = tmp_path / "web.json"
        path.write_text(
            json.dumps(
                {"web": {"client_id": "123", "client_secret": "GOCSPX-", "redirect_uris": []}}
            )
        )
        data = load_client_secret(path)
        assert "web" in data


class TestExtractClientIdSecret:
    def test_installed(self):
        data = {
            "installed": {
                "client_id": "abc",
                "client_secret": "GOCSPX-abc",
            }
        }
        cid, cs = extract_client_id_secret(data)
        assert cid == "abc"
        assert cs == "GOCSPX-abc"

    def test_web(self):
        data = {"web": {"client_id": "web-abc", "client_secret": "GOCSPX-web"}}
        cid, cs = extract_client_id_secret(data)
        assert cid == "web-abc"
        assert cs == "GOCSPX-web"

    def test_missing_raises(self):
        with pytest.raises(ClientSecretError):
            extract_client_id_secret({})

    def test_missing_client_id_raises(self):
        with pytest.raises(ClientSecretError):
            extract_client_id_secret({"installed": {"client_secret": "x"}})


class TestScopesMissing:
    def test_all_missing_when_empty(self):
        assert scopes_missing([]) == GOOGLE_SCOPES_ALL

    def test_none_missing_when_all_present(self):
        assert scopes_missing(list(GOOGLE_SCOPES_ALL)) == []

    def test_partial(self):
        partial = [GOOGLE_SCOPES_ALL[0]]
        missing = scopes_missing(partial)
        assert GOOGLE_SCOPES_ALL[0] not in missing
        assert len(missing) == len(GOOGLE_SCOPES_ALL) - 1
