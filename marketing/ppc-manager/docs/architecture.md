# PPC Manager — Architecture

A walkthrough of how the plugin is put together: directory layout, MCP servers, the shared auth library, hooks, and how skills invoke the MCPs.

---

## Directory layout

```
ppc-manager/
├── .claude-plugin/plugin.json          # Plugin manifest + userConfig schema
├── .mcp.json                           # 4 MCP server registrations
├── README.md                           # Plugin overview
├── CHANGELOG.md
├── LICENSE                             # MIT (plugin-level)
├── Makefile                            # make test / test-live / lint / coverage / install
├── requirements.txt                    # Runtime Python deps
├── requirements-dev.txt                # Dev deps (pytest, freezegun, ...)
├── settings.json                       # {}
│
├── agents/
│   └── campaign-auditor.md             # Sub-agent for campaign-audit skill
│
├── hooks/
│   ├── hooks.json                      # SessionStart + Stop hook definitions
│   └── scripts/
│       ├── ensure-venv.sh + .ps1       # Bootstraps Python venv in CLAUDE_PLUGIN_DATA
│       ├── check-credentials.sh + .ps1 # Runs token_validator.py --quiet at session start
│       └── suggest-next-skill.sh + .ps1
│
├── bin/
│   ├── python_shim.sh                  # Runtime Python interpreter resolver
│   └── python_shim.ps1
│
├── scripts/                            # Shared helpers used by MCP servers + oauth scripts
│   ├── oauth_google.py                 # CLI: Google OAuth InstalledAppFlow → vault
│   ├── oauth_meta.py                   # CLI: Meta loopback OAuth → vault
│   ├── token_validator.py              # CLI: Smoke-tests every account in the vault
│   ├── utm_builder.py                  # UTM URL generator (no API)
│   ├── keyword_clusterer.py            # TF-IDF keyword clustering (no API)
│   ├── campaign_audit_scorer.py        # Heuristic scoring for campaign-audit
│   └── lib/
│       ├── vault.py                    # PPCVault — Fernet + PBKDF2 encrypted JSON
│       ├── ppc_auth.py                 # PPCAuth facade (all MCP servers depend on this)
│       ├── masking_logger.py           # Stderr logger with token masking
│       ├── google_helpers.py           # client_secret parsing + scope helpers
│       └── meta_helpers.py             # Meta Graph API helper calls
│
├── mcp_servers/
│   ├── common/                         # Shared across every MCP server
│   │   ├── errors.py                   # Typed exceptions (ToolError, NotFoundError, ...)
│   │   ├── logger.py                   # Wrapper for masking_logger
│   │   └── formatting.py               # Markdown table helpers
│   ├── gtm/                            # ~15 GTM tools (ported from gtm-mcp)
│   │   ├── server.py
│   │   └── tools/{containers,tags,triggers,variables,versions}.py
│   ├── ga4/                            # ~12 GA4 tools (ported from google-analytics-mcp)
│   │   ├── server.py
│   │   └── tools/{admin,reporting,events}.py
│   ├── google_ads/                     # ~25 Google Ads tools (subset of google-ads-plugin)
│   │   ├── server.py
│   │   └── tools/{accounts,campaigns,ad_groups,ads,keywords,reporting}.py
│   └── meta/                           # ~20 Meta tools (built from scratch on facebook_business)
│       ├── server.py
│       └── tools/{accounts,campaigns,ad_sets,ads,audiences,insights,pixels,capi}.py
│
├── skills/                             # 23 skills (22 scaffolded + new oauth-setup)
│   ├── oauth-setup/                    # NEW — entry-point skill
│   ├── gtm-setup/ gtm-datalayer/ gtm-tags/
│   ├── ga4-setup/ ga4-events/
│   ├── google-ads-account-setup/ google-search-campaign/ google-pmax-campaign/
│   ├── google-ads-copy/ display-ad-specs/
│   ├── meta-pixel-setup/ meta-capi-setup/ meta-events-mapping/
│   ├── meta-audience-builder/ meta-creative-brief/ meta-ads-copy/
│   ├── keyword-research/ campaign-audit/ utm-builder/ landing-page-copy/ youtube-campaign/
│   │   # Each contains: SKILL.md, reference.md, LICENSE.txt,
│   │   #                templates/output-template.md, examples/example-output.md
│
├── docs/
│   ├── credentials.md
│   └── architecture.md (this file)
│
└── tests/
    ├── conftest.py
    ├── unit/                           # Mocked unit tests for vault, ppc_auth, oauth scripts
    ├── integration/                    # Vault lifecycle + gated live API tests
    └── lint/                           # Skill structure, manifest, AU-English checks
```

---

## Data flow — skill invocation

1. **User runs `/ppc-manager:gtm-setup`.**
2. Claude loads `skills/gtm-setup/SKILL.md` and starts executing phases.
3. Phase 1 calls `ppc-gtm:list_accounts`. Claude sends the tool call to the `ppc-gtm` MCP server.
4. Inside the MCP server:
   - `mcp_servers/gtm/server.py` receives the call.
   - `get_auth()` lazily instantiates a `PPCAuth` from environment variables (`PPC_VAULT_PATH`, `PPC_VAULT_PASSPHRASE`).
   - `containers.list_accounts` tool calls `auth.get_gtm_service(google_account)`.
   - `get_gtm_service` calls `get_google_credentials` which:
     - Loads the vault (from memory if cached, otherwise decrypts `tokens.enc`).
     - Reads the Google account entry.
     - If access token is near expiry, refreshes via `creds.refresh(Request())`.
     - Writes new access token back to the vault if refreshed.
     - Returns a live `Credentials` object.
   - Builds a `googleapiclient.discovery.Resource` for Tag Manager v2.
   - Calls the GTM API.
   - Wraps any SDK exception in `wrap_http_error` → typed `ToolError`.
   - Returns a dict to the MCP framework.
5. Claude receives the structured response and proceeds with Phase 2.
6. Every subsequent tool call follows the same path. The vault is decrypted once per MCP server process; subsequent calls use the in-memory cache until the process dies.

---

## Bootstrap flow — SessionStart

1. User starts Claude Code.
2. The `ensure-venv.sh` hook runs:
   - Checks for Python 3.11+ on PATH.
   - Creates `${CLAUDE_PLUGIN_DATA}/venv/` if missing.
   - Compares `requirements.txt` against `requirements.stamp`; if they differ, runs `pip install -r requirements.txt`.
   - Writes the resolved interpreter path to `${CLAUDE_PLUGIN_DATA}/python_path.txt` so the MCP shim can find it.
3. The `check-credentials.sh` hook runs:
   - Reads the python path file.
   - Invokes `token_validator.py --quiet --json`.
   - If the exit code is non-zero, emits a `systemMessage` JSON with a remediation hint.
4. Claude starts the four MCP servers via `.mcp.json`:
   - Each server's `command` is `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh` (or `.ps1` on Windows).
   - The shim reads the interpreter path from `python_path.txt` and execs it on the MCP server's `server.py`.
   - Environment variables inject `PPC_VAULT_PATH`, `PPC_VAULT_PASSPHRASE`, `CLAUDE_PLUGIN_OPTION_*`.
5. Each server logs "PPCAuth initialised" to stderr on first tool call.

---

## MCP server tool surface

| Server | Modules | Approx tool count |
|---|---|---|
| `ppc-gtm` | containers, tags, triggers, variables, versions | 15 |
| `ppc-ga4` | admin, reporting, events | 12 |
| `ppc-google-ads` | accounts, campaigns, ad_groups, ads, keywords, reporting | 20 |
| `ppc-meta` | accounts, campaigns, ad_sets, ads, audiences, insights, pixels, capi | 20 |
| **Total** | | **~67** |

Every tool:

1. Accepts an `account_label` / `google_account` parameter defaulting to `"default"`.
2. Calls `get_auth().get_*_client(label)` to fetch a live, refreshed client.
3. Wraps any upstream SDK call in try/except and raises a typed error on failure.
4. Returns a dict (not a raw SDK object) so the MCP framework can serialise it cleanly.

---

## The shared auth library (`scripts/lib/ppc_auth.py`)

The single file every MCP server depends on. Key design decisions:

- **One `PPCAuth` instance per server process.** Created lazily the first time any tool is called. Holds a `PPCVault` which caches the decrypted JSON in memory.
- **No module-level state.** All state lives on the `PPCAuth` instance.
- **Environment-driven construction.** `PPCAuth.from_env()` reads `PPC_VAULT_PATH` and `PPC_VAULT_PASSPHRASE` from env vars injected by `.mcp.json`.
- **Refresh-on-read semantics.** Every `get_google_credentials` call checks expiry and refreshes if needed, writing back to the vault under a file lock.
- **Typed exceptions.** `AuthError` for anything the user should see, `VaultError` for file-system issues.
- **No direct Google / Meta SDK imports at module load.** They're inside methods so the file can be imported in test contexts without the SDK installed.

---

## Hook system

The plugin ships three hook scripts:

| Event | Script | What it does |
|---|---|---|
| SessionStart | `ensure-venv.sh` | Bootstraps the Python venv. Max 180s timeout. |
| SessionStart | `check-credentials.sh` | Runs `token_validator.py --quiet --json`. Max 15s timeout. |
| Stop | `suggest-next-skill.sh` | Greps the transcript for the most recent ppc-manager skill and suggests a downstream skill. Max 5s timeout. |

All scripts have `.ps1` siblings for Windows users without Git Bash. All scripts are designed to **never block** — they emit `systemMessage` JSON on failures rather than returning non-zero.

---

## Test strategy

- **Unit tests** (`tests/unit/`) — 90%+ coverage target on `scripts/lib/`. Everything mocked, no network.
- **Integration tests** (`tests/integration/`) — vault lifecycle (encrypt/decrypt, atomic write, passphrase rotation). No network.
- **Live tests** (`tests/integration/test_live_*.py`) — gated behind `PPC_MANAGER_LIVE_TESTS=1`. Hit real sandbox accounts. Only run in CI when secrets are available.
- **Lint tests** (`tests/lint/`) — every `SKILL.md` validates against the schema; `plugin.json` and `marketplace.json` validate against published Claude Code schemas; Australian English check on skill content.

Run via `make test` (default: unit + integration-local + lint) or `make test-live` (live API tests).

---

## Dependency graph

```
skills/*.md
   │
   ▼ invoke via /ppc-manager:<skill-name>
   │
   ▼ uses MCP tools
   │
   ▼ ppc-gtm / ppc-ga4 / ppc-google-ads / ppc-meta (each a separate Python process)
   │
   ▼ each imports mcp_servers.{platform}.tools.*
   │
   ▼ each tool calls get_auth().get_<platform>_*()
   │
   ▼ ppc_auth.PPCAuth
   │
   ▼ lib.vault.PPCVault  ──── reads/writes ────▶  ${CLAUDE_PLUGIN_DATA}/tokens.enc
   │
   ▼ cryptography.fernet + google-auth / facebook_business SDKs
   │
   ▼ HTTPS to Google / Meta APIs
```

---

## Extending the plugin

To add a new platform (say TikTok Ads):

1. Add a new `mcp_servers/tiktok/` directory with `server.py` + `tools/*.py`.
2. Add auth support to `scripts/lib/ppc_auth.py` — a `get_tiktok_client(label)` method.
3. Extend the vault schema — add a `tiktok.accounts` section.
4. Extend `scripts/oauth_tiktok.py` to run the TikTok OAuth flow and write to the vault.
5. Register `ppc-tiktok` in `.mcp.json`.
6. Add new userConfig fields for `tiktok_app_id`, `tiktok_app_secret` if needed.
7. Add skill(s) in `skills/` that invoke the new MCP tools.
8. Add tests to `tests/unit/` and `tests/lint/`.

To add a new skill for an existing platform:

1. Create `skills/<new-skill>/` directory.
2. Write `SKILL.md` following the brand-manager convention (frontmatter + phases + behavioural rules + edge cases).
3. Write `reference.md`, `LICENSE.txt`, `templates/output-template.md`, `examples/example-output.md`.
4. Add the skill to `suggest-next-skill.sh` hook for chaining.
5. Add the skill to `tests/lint/test_skill_structure.py` automatically picks it up.

---

## Versioning

- **Plugin version** (`plugin.json` `version`): bumps on any feature addition or breaking change.
- **Marketplace version** (`marketplace.json` `metadata.version`): bumps on any plugin addition/removal.
- Follow semver: major for breaking changes, minor for new skills / tools, patch for fixes and doc updates.
