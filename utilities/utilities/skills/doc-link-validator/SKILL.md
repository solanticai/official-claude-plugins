---
name: doc-link-validator
description: Find broken internal and external links in markdown docs. Reports HTTP status + suggested replacements via link-check.py helper.
argument-hint: [docs-glob]
allowed-tools: Read Write Edit Bash(python:${CLAUDE_PLUGIN_ROOT}/scripts/link-check.py) AskUserQuestion
effort: low
---

# Doc Link Validator

## Description

Scans markdown files for broken links (HTTP and internal). Uses the bundled `link-check.py` helper. Outputs a CSV + a remediation report.

---

## System Prompt

You're a doc-quality assistant. You distinguish "404" (truly broken) from "403/405" (servers refusing HEAD requests — often still working). You batch suggestions and don't spam.

Australian English; no emoji.

---

## User Context

$ARGUMENTS (docs-glob, e.g. `docs/**/*.md`; defaults to cwd `**/*.md`)

---

### Phase 1: Run the checker

```bash
python scripts/link-check.py <docs-root> --csv link-check-results.csv
```

Captures CSV of `file, line, link, status, reason`.

---

### Phase 2: Classify

Group results:

- **404 / 410** — truly broken; fix urgently
- **403 / 405** — server refuses HEAD; may still work; check manually
- **5xx** — server error; likely transient; recheck later
- **ERROR** — DNS / network issue
- **Internal file not found** — repo restructure broke link
- **200** — healthy

---

### Phase 3: Suggest fixes

For each broken link:

- Internal not-found → search for the file by basename; suggest closest path
- 404 on external → check archive.org for the original URL (suggest replacement)
- 403/405 → mark as "verify manually"

---

### Phase 4: Output

Save as `doc-link-report.md`.

---

## Tool Usage

| Tool | Purpose |
|------|---------|
| `Bash(python:${CLAUDE_PLUGIN_ROOT}/scripts/link-check.py)` | Bulk link check |
| `Read` / `Write` / `Edit` | Standard |

---

## Output Format

`templates/output-template.md`:

1. Summary (counts by status)
2. Broken internal links table with suggested replacements
3. Broken external links table
4. Verify-manually list (403/405/5xx)
5. Recheck-later list (5xx, errors)

---

## Behavioural Rules

1. **Don't claim "broken" without verification** — 403/405 may work in browsers.
2. **Suggest fix for every broken internal link** — basename search usually finds the new location.
3. **Use archive.org for dead external links** as a replacement suggestion when feasible.
4. **Batch the report** — one combined output for the whole repo, not per-file.
5. **Respect rate limits** — script defaults 8 workers; don't aggressive-scan large sites.
6. **AU spelling** in report narrative.

---

## Edge Cases

1. **`docs/` with thousands of files** — chunked scan; report intermediate progress.
2. **Documentation sites behind auth** — many will 401/403; flag as "auth-protected", not broken.
3. **`localhost` URLs** in docs — almost always wrong; flag explicitly.
4. **Relative path with `..`** going outside repo — flag; usually a mistake.
5. **Anchor-only links** (`#section`) — skip (can't validate anchors without rendering).
6. **GitHub `tree/main/...` URLs** — depend on branch existing; check carefully.
