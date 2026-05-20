# Repo Snapshot — Reference Material

## Framework Detection Heuristics

| Indicator file | Framework |
|---------------|-----------|
| `next.config.js` / `next.config.ts` | Next.js |
| `remix.config.js` | Remix |
| `astro.config.mjs` | Astro |
| `svelte.config.js` | SvelteKit |
| `nuxt.config.ts` | Nuxt |
| `vite.config.ts` (no framework above) | Vite + Vue or React |
| `app.json` + `babel.config.js` | Expo / React Native |
| `manage.py` + `settings.py` | Django |
| `Gemfile` + `config/routes.rb` | Rails |
| `pom.xml` | Maven (Java) |
| `build.gradle` | Gradle (Java/Kotlin) |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml` (poetry/uv/hatch) | Modern Python |
| `requirements.txt` only | Older Python |
| `composer.json` | PHP / Laravel |
| `Pipfile` | Pipenv (Python) |

---

## Build Tool Detection

| File | Tool |
|------|------|
| `package-lock.json` | npm |
| `yarn.lock` | Yarn |
| `pnpm-lock.yaml` | pnpm |
| `bun.lockb` | Bun |
| `Cargo.lock` | cargo |
| `poetry.lock` | Poetry |
| `uv.lock` | uv |
| `Gemfile.lock` | bundler |
| `composer.lock` | composer |

---

## Test Framework Detection

| Pattern | Framework |
|---------|-----------|
| `vitest.config.ts` / `vitest` in package.json | Vitest |
| `jest.config.js` | Jest |
| `playwright.config.ts` | Playwright |
| `cypress.config.ts` | Cypress |
| `mocha` in package.json + `test/` | Mocha |
| `pytest.ini` / `pyproject.toml [tool.pytest]` | pytest |
| `tox.ini` | Tox |
| `*_test.go` files | Go test |
| `spec/` + `Gemfile` has rspec | RSpec |

---

## LOC Counting Tips

```bash
# JS/TS/JSX/TSX
find . -path ./node_modules -prune -o \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -print | xargs wc -l | sort -rn | head -20

# Python (exclude virtualenv)
find . -path "*/.venv" -prune -o -name "*.py" -print | xargs wc -l | sort -rn | head -20

# Go (exclude vendor)
find . -path ./vendor -prune -o -name "*.go" -print | xargs wc -l | sort -rn | head -20

# Rust
find . -path ./target -prune -o -name "*.rs" -print | xargs wc -l | sort -rn | head -20

# Markdown
find . -name "node_modules" -prune -o -name "*.md" -print | xargs wc -l | sort -rn | head -20
```

Adjust prune list per repo.

---

## Snapshot Sections by Audience

### New-hire (engineering)

- Folder tree with annotations
- Top files by LOC (focus on those they'll edit)
- Key conventions (CLAUDE.md, CONTRIBUTING, code style)
- "Read these 3 files first"

### Investor / DD

- Stack + scale
- Activity (commits/month, contributors)
- Security signals (dependency age, auth setup, secret-management)
- Test coverage signals (test framework + ratio)

### Future-you / handoff

- Why decisions were made (link to ADRs / docs)
- Where bodies are buried (known-hard areas)
- What's queued in roadmap

### External auditor

- Security configuration files
- Dependency manifest
- Recent CVE-relevant updates
- Access-control / RLS / auth flow files

---

## Common Bus-Factor Risks

- Single contributor (bus-factor 1)
- All commits within last 90 days from one author
- No PR review history
- No documented runbook for common ops
- No SECURITY.md / no documented vulnerability disclosure
- Dependencies pinned but never updated (last update > 12 months)
- Only one person has deploy permissions

Surface these explicitly in the snapshot output.
