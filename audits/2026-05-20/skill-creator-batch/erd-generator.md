# erd-generator — Skill Audit

**Path:** `engineering/database-design/skills/erd-generator/`
**Date:** 2026-05-20
**Rubric:** 8 dims / 115 pts

---

## Scores

| # | Dimension | Max | Score | Notes |
|---|-----------|-----|-------|-------|
| 1 | Metadata / Frontmatter | 15 | 14 | `name`, `description` (159 chars), `argument-hint`, `allowed-tools`, `effort` all present (SKILL.md:1-7). Description front-loads use case. Missing optional `license` field but LICENSE.txt MIT present. |
| 2 | Scope / Boundaries | 15 | 14 | Tight remit: ERD only, two formats. Edge cases enumerated (SKILL.md:147-153). Hand-off to migration design implied but not explicit. |
| 3 | Conciseness | 15 | 15 | SKILL.md 153 lines (well under 500). Dense reference correctly extracted to `reference.md` (123 lines). |
| 4 | Architecture / File Layout | 15 | 13 | Standard layout (SKILL.md, reference.md, templates/, examples/, LICENSE.txt). `Bash(bash:scripts/schema-introspect.sh)` (SKILL.md:5) references plugin-level `scripts/` — script exists at `database-design/scripts/schema-introspect.sh`, not in skill folder. Path is relative-to-skill so will resolve incorrectly when CWD differs; should be `${CLAUDE_PLUGIN_ROOT}/scripts/schema-introspect.sh`. |
| 5 | Content Quality | 20 | 19 | 6 phases (SKILL.md:36-110), behavioural rules (136-144), edge cases (147-153). Both Mermaid + DBML produced every time (rule 1). Cardinality + optionality + ON DELETE all explicit (Phase 3, lines 58-66). Example (example-output.md) demonstrates all six ON DELETE patterns in DBML refs (128-132). |
| 6 | Tools / Permissions | 10 | 7 | Allowed-tools narrow and appropriate (Read, Write, Edit, Bash with specific script). However Bash matcher `Bash(bash:scripts/...)` uses unconventional syntax — Claude Code permission matchers normally use `Bash(bash scripts/...:*)` or full command prefix. May not actually match invocations. Missing `Glob`/`Grep` could hurt schema exploration. |
| 7 | Testing / Examples | 15 | 14 | One realistic example (jobs-and-quotes multi-tenant SaaS, 154 lines) with 8 entities, Mermaid + DBML + notation legend + 3 open questions. AUD currency demonstrates AusE context. Only one example — could use a second covering live-Supabase pathway. |
| 8 | Standards Compliance | 10 | 9 | AusE used (`behaviour`, `optimise`-adjacent). Snake_case enforced. `argument-hint` present. MIT LICENSE.txt. Output filename `erd.md` (SKILL.md:110) is reasonable but template doesn't restate it. |

**Total: 105 / 115 → Grade A**

---

## Special Checks

- **(a) `Bash(bash:scripts/schema-introspect.sh)` resolution:** Script lives at `engineering/database-design/scripts/schema-introspect.sh` (plugin-level, confirmed exists, 72 lines). The matcher in `allowed-tools` (SKILL.md:5) uses a non-standard path syntax that will likely fail to match when Claude invokes the script — needs `${CLAUDE_PLUGIN_ROOT}` prefix or a properly-formed Bash permission matcher. **Functional risk.**
- **(b) Mermaid + DBML dual output:** Both required by behavioural rule 1 (SKILL.md:138). Template (output-template.md:18-45) and example (example-output.md:25-133) both include both. Confirmed.
- **(c) Cardinality + ON DELETE coverage:** Cardinality enumerated in Phase 3 (SKILL.md:62), reference.md:77-86. ON DELETE behaviour in Phase 3 (SKILL.md:66), reference.md:89-97 (CASCADE/RESTRICT/SET NULL/SET DEFAULT/NO ACTION), demonstrated in example DBML refs (example-output.md:128-132). Comprehensive.

---

## Top 3 P0 Fixes

1. **Fix Bash permission matcher syntax (SKILL.md:5).** Change `Bash(bash:scripts/schema-introspect.sh)` to `Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/schema-introspect.sh:*)`. Current form is non-standard and the relative path will resolve from CWD, not the plugin root — script invocation will fail in most sessions.
2. **Add explicit script-path note in Phase 1 (SKILL.md:38).** Replace `bash scripts/schema-introspect.sh` with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/schema-introspect.sh` so the model invokes the correct absolute path and matches the (corrected) permission matcher.
3. **Add a live-schema example.** Current single example (jobs-and-quotes) covers narrative-input pathway only. Add `examples/example-live-schema.md` demonstrating the Supabase-MCP introspection pathway end-to-end (digest → entity extraction → Mermaid + DBML), so the schema-introspect tool path has visible test coverage.

---

## Minor Suggestions

- Document the output filename (`erd.md`) in the template header so users know the canonical artefact name.
- Add Glob/Grep to allowed-tools to support exploring migration files when working from a code repo rather than live DB.
- Cross-reference `database-design/skills/migration-design` (if it exists) as the natural next step after ERD finalisation.
