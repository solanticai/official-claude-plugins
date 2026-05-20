"""Shared pytest fixtures for ppc-manager tests."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# Ensure the plugin scripts/ directory is on sys.path for unit tests.
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture()
def tmp_vault_path(tmp_path):
    """Return a path inside tmp_path where a vault file can live."""
    return tmp_path / "tokens.enc"


@pytest.fixture()
def passphrase():
    return "correct horse battery staple"


@pytest.fixture()
def sample_vault_data():
    return {
        "version": 1,
        "updated_at": "2026-04-11T00:00:00+00:00",
        "google": {
            "client_secret": "GOCSPX-test-secret",
            "accounts": {
                "default": {
                    "label": "default",
                    "email": "john@anthril.com",
                    "client_id": "123.apps.googleusercontent.com",
                    "refresh_token": "1//0g-test-refresh",
                    "access_token": "ya29.test-access",
                    "access_token_expires_at": "2026-04-11T01:00:00+00:00",
                    "scopes": [
                        "https://www.googleapis.com/auth/tagmanager.edit.containers",
                        "https://www.googleapis.com/auth/tagmanager.readonly",
                        "https://www.googleapis.com/auth/analytics.readonly",
                        "https://www.googleapis.com/auth/analytics.edit",
                        "https://www.googleapis.com/auth/adwords",
                    ],
                }
            },
        },
        "google_ads": {
            "accounts": {
                "acme": {
                    "label": "acme",
                    "customer_id": "1234567890",
                    "login_customer_id": "9876543210",
                    "linked_google_account": "default",
                }
            }
        },
        "meta": {
            "app_secret": "meta-test-secret",
            "accounts": {
                "default": {
                    "label": "default",
                    "user_id": "111",
                    "user_name": "Test User",
                    "long_lived_user_token": "EAABtest-long-token",
                    "long_lived_user_token_expires_at": "2026-06-10T00:00:00+00:00",
                    "ad_accounts": [
                        {"id": "act_111", "name": "Acme", "currency": "AUD"},
                    ],
                }
            },
        },
    }


@pytest.fixture()
def fake_client_secret_file(tmp_path):
    """Write a fake Google OAuth Desktop client_secret JSON and return the path."""
    path = tmp_path / "client_secret.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "123.apps.googleusercontent.com",
                    "project_id": "ppc-manager-test",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_secret": "GOCSPX-test-secret",
                    "redirect_uris": ["http://localhost"],
                }
            }
        )
    )
    return path
