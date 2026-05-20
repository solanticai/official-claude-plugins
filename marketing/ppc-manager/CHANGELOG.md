# Changelog

All notable changes to the ppc-manager plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-11

### Added
- `oauth-setup` skill — single entry point walking users through Google (GTM, GA4, Google Ads) and Meta OAuth via a local loopback browser flow.
- Encrypted credential vault (`${CLAUDE_PLUGIN_DATA}/tokens.enc`, Fernet + PBKDF2-SHA256) unlocked by a keychain-held passphrase.
- Four bundled Python MCP servers: `ppc-gtm`, `ppc-ga4`, `ppc-google-ads`, `ppc-meta`.
- 3 Google Tag Manager skills: `gtm-setup`, `gtm-datalayer`, `gtm-tags`.
- 2 Google Analytics 4 skills: `ga4-setup`, `ga4-events`.
- 5 Google Ads skills: `google-ads-account-setup`, `google-search-campaign`, `google-pmax-campaign`, `google-ads-copy`, `display-ad-specs`.
- 6 Meta Ads skills: `meta-pixel-setup`, `meta-capi-setup`, `meta-events-mapping`, `meta-audience-builder`, `meta-creative-brief`, `meta-ads-copy`.
- 5 cross-platform skills: `keyword-research`, `campaign-audit`, `utm-builder`, `landing-page-copy`, `youtube-campaign`.
- `campaign-auditor` sub-agent for deep PPC audits.
- SessionStart hooks — bootstraps Python venv, validates credentials.
- Stop hook — suggests logical next skills.
- Plugin-level scripts: `oauth_google.py`, `oauth_meta.py`, `token_validator.py`, `utm_builder.py`, `keyword_clusterer.py`, `campaign_audit_scorer.py`.
- Shared auth library (`scripts/lib/ppc_auth.py`, `vault.py`, `masking_logger.py`, `google_helpers.py`, `meta_helpers.py`).
- Unit tests for vault, ppc_auth, masking_logger, token_validator, oauth scripts, and google_helpers.
- Lint tests for skill structure, manifests, and Australian English conventions.
- Integration tests for vault lifecycle (encrypt/decrypt round-trip, passphrase rotation, multi-account upsert).
- Marketplace registration in `anthril-claude-plugins`.
