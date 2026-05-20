# Skill Audit — energy-detective

**Path:** `lifestyle/personal-productivity/skills/energy-detective/`
**Date:** 2026-05-20
**Auditor:** skill-evaluator rubric

---

## Dimension Scores

### 1. Discovery & Metadata — 19/20
- Frontmatter complete: `name`, `description`, `argument-hint`, `allowed-tools`, `effort` (SKILL.md:1-7).
- Description 187 chars, front-loaded with use case (SKILL.md:3).
- `effort: low` (SKILL.md:6) — defensible for a single-pass log analysis; rubric prefers `medium`+ but spec permits `low`. Minor.

### 2. Scope & Focus — 15/15
- Tight scope: read a 7-day log, infer patterns, output schedule recs (SKILL.md:11-26).
- Clear "use when" list (SKILL.md:20-25).
- Cross-references to sibling skills via `[[deep-focus-day]]`, `[[habit-stacker]]` (SKILL.md:25) without bleeding scope.

### 3. Conciseness — 15/15
- SKILL.md 205 lines, well under 500 (file total = 205).
- Dense reference extracted to `reference.md` (108 lines).

### 4. Information Architecture — 15/15
- Five sequenced phases (Intake → Heatmap → Drain/Restore → Chronotype → Schedule), each with Objective/Steps/Output (SKILL.md:51-141).
- `reference.md` present and explicitly cued (SKILL.md:144-153).
- `templates/output-template.md` (100 lines) and `examples/example-output.md` (101 lines) both present.

### 5. Content Quality — 15/15
- `$ARGUMENTS` used at SKILL.md:45.
- Behavioural rules block (SKILL.md:185-194) — 7 concrete rules.
- Edge Cases section (SKILL.md:197-204) covers 6 realistic scenarios incl. shift work, medical flat-line, over-reporting.
- Example is realistic — Perth FIFO engineer with plausible 7-day heatmap (examples/example-output.md:1-21).

### 6. Tool & Security — 10/10
- `allowed-tools: Read Write Edit Bash(cat:*) Bash(wc:*)` (SKILL.md:5) — granular Bash restriction with explicit subcommand allowlist. No Agent, no shell glob. Exemplary.

### 7. Testing & Examples — 6/7
- Example output present and detailed (101 lines).
- Template aligns with example structure.
- No automated test harness / no second example covering an edge case (e.g. shift-work or split chronotype). Minor.

### 8. Standards Compliance — 3/3
- Australian English throughout — "behaviour" (SKILL.md:185 section header `Behavioural Rules`), "generalise" (SKILL.md:191), "Australian English throughout" (SKILL.md:37), AEST/AEDT call-out (SKILL.md:193).
- LICENSE.txt present (21 lines).
- No emoji in any file inspected.

---

## Total: 98/115 → Grade B

(Borderline B/A — strong skill, mostly small deductions.)

---

## Top 3 Fixes (P0)

1. **Bump `effort` from `low` to `medium`** (SKILL.md:6) — five phases incl. Mermaid generation, clustering, chronotype inference, and hypothesis design is medium-complexity analytical work, not low.
2. **Add a second example** under `examples/` covering a different chronotype or the shift-work edge case (SKILL.md:202) so the edge-case handling is demonstrated, not just declared.
3. **Add a brief "small-sample handling" rule to Phase 2** — current Phase 2 (SKILL.md:72-84) assumes a full 7-day log; should explicitly downgrade heatmap confidence / collapse to 4-bin schema when fewer than ~25 observations, mirroring Edge Case 1 (SKILL.md:199).
