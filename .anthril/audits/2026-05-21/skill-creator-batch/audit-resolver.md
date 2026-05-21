# Skill Evaluator Report — audit-resolver

**Date:** 2026-05-21
**Skill path:** `utilities/utilities/skills/audit-resolver/`
**Companion command:** `utilities/utilities/commands/audit-resolve.md`

---

## Scores

| Dim | Score | Notes |
|---|---|---|
| Discovery (20) | 19 | Clear front-loaded description (SKILL.md:3); strong trigger list (:16-21); name + argument-hint match; companion command improves discoverability. Minor: description mentions "audit" but not "fix execution" keyword density could rise. |
| Scope (15) | 15 | Tight scope: read audit → triage → execute → verify → ledger. No bleed into commit/push/branch (SKILL.md:22, 260, 277). |
| Conciseness (15) | 13 | SKILL.md = 301 lines (well under 500). Reference dense + extracted appropriately (reference.md:1-133). Slight redundancy between SKILL.md "Behavioural Rules" (:275-285) and Phase 5 (:163-198), but acceptable. |
| Architecture (15) | 15 | 7 phases each with Objective / Steps / Output (Phases 1-7, SKILL.md:54-246). Resumability documented (reference.md:124-133). Ledger-as-resume-state pattern explicit (SKILL.md:271; reference.md:124-133). |
| Content (15) | 14 | Edge cases = 12 (SKILL.md:288-301) — exceeds ≥10 requirement. Category→strategy map (reference.md:7-29). Verifier matrix (reference.md:48-77). Sub-skill dispatch map (reference.md:81-97). Example output realistic. Minor: example-output.md truncated to 50 lines viewed but file is 135 lines. |
| Tool (10) | 10 | Special checks pass: `AskUserQuestion` present (SKILL.md:5) — used in Phase 3 gate (:125) and HUMAN-INPUT (:188-191) and Phase 4 dirty-tree (:147). `Agent` present (SKILL.md:5) — used in SUB-SKILL (:178) and PLAN-FIRST (:184). Deliberate omission of `git commit/push/reset` and `rm` called out (SKILL.md:260). Granular Bash allowlist (`git:diff`, `git:status`, `git:log`, `git:stash`, etc.). |
| Testing (7) | 5 | Two scripts present (parse-audit-report.sh, verify-stack.sh) — both well-commented + handle edge cases (heuristic parse fallback, no-verifier-detected exit-0). No standalone unit tests for the scripts themselves; verifier matrix tested only via skill invocation. |
| Standards (3) | 3 | Australian English ("optimise" SKILL.md:28, "behaviour"-adjacent terms); no emoji detected; reaffirmed at SKILL.md:32 + Behavioural Rule 8 (:284). |
| Activation (10) | 9 | Companion command (commands/audit-resolve.md) provides slash entry. Description triggers on "audit", "findings", "fix". No `paths:` glob (could auto-activate on `audits/**/*.md`). |
| Anti-patterns (5) | 5 | No emoji, no "comprehensive"/"robust" filler, no fake confidence scores, no commit-on-behalf-of-user. Halts on verifier failure (:198). |

---

## Total: 108 / 115 — Grade A

---

## Special-Check Verification

(a) `AskUserQuestion` in allowed-tools — PASS (SKILL.md:5; used :125, :147, :188)
(b) `Agent` in allowed-tools — PASS (SKILL.md:5; used :178 SUB-SKILL, :184 PLAN-FIRST)
(c) Deliberate omissions of `git commit/push/reset`, `rm` called out — PASS (SKILL.md:260; Behavioural Rule 1 :277)
(d) Australian English; no emoji — PASS (:32, :284)
(e) SKILL.md ≤ 500 lines — PASS (301 lines)
(f) Per-phase Objective / Steps / Output — PASS (Phases 1-7, though Phase 5 substitutes "Steps per batch" + Phase 6 substitutes "When" — minor style drift, structurally equivalent)
(g) Edge cases ≥ 10 — PASS (12 listed, :290-301)
(h) Ledger-as-resume-state in reference.md — PASS (reference.md:124-133)

---

## Command + Skill Alignment

`commands/audit-resolve.md` correctly:
- Forwards flags verbatim (commands/audit-resolve.md:25-32)
- Defers heavy lifting to skill (:19, :55)
- Mirrors error handling (no report found → suggest `/utilities:plan-completion-audit`; matches SKILL.md:61)
- Provides realistic invocation examples (:36-51)

Minor drift: command flow step 3 says "Confirm target" via AskUserQuestion before dispatch, but the skill itself also runs an AskUserQuestion in Phase 3. Risk: double-prompt. Suggest the command skip its step-3 confirm when handing off to the skill (let the skill own that gate) — or document explicitly that the command's step-3 is a coarse gate ("right report?") and Phase 3 is a fine gate ("right plan?").

---

## Top 3 Fixes (P0)

1. **Double-confirmation risk between command and skill.** `commands/audit-resolve.md:15` runs an AskUserQuestion to confirm the target report, then `SKILL.md:125` runs another AskUserQuestion to confirm the plan. Either remove the command's confirm (the skill owns it) or scope it explicitly to "right report?" vs "right plan?" with a one-line note in both files. Currently the user gets prompted twice for what feels like the same thing.

2. **Phase 5 + Phase 6 structural drift from the Objective/Steps/Output pattern.** SKILL.md:156-198 uses "Steps per batch" instead of "Steps" and never closes with an "Output" sub-section; SKILL.md:201-219 uses "When" instead of "Steps" header. The rubric expects uniform Objective/Steps/Output per phase. Rename to canonical headings and add an "Output" line to each (e.g. Phase 5 Output: "Batch executed, verifier run, ledger Execution Log appended"; Phase 6 Output: "Re-audit diff at `audits/<date>/audit-resolver-reaudit-diff.md`").

3. **No test harness for the helper scripts.** `scripts/parse-audit-report.sh` is heuristic and `scripts/verify-stack.sh` has stack-detection logic — both are silent-failure prone. Add `tests/test_parse_audit_report.sh` with at least 3 fixtures (table-format report, bullet-format report, empty report) asserting expected TSV output. Currently Testing scores 5/7 because the scripts ship without coverage even though they're load-bearing.

---

## Lesser fixes

- Add `paths:` frontmatter glob (e.g. `paths: audits/**/*.md`) so audit reports auto-suggest the skill (+1 Activation).
- example-output.md only viewed first 50 lines in this audit pass — verify it covers Re-audit Diff section (template has it at :62-72).
- `Bash(test:*)` in allowed-tools (SKILL.md:5) is ambiguous — clarify whether this is POSIX `test`/`[`, or a generic placeholder for verifier commands. Consider replacing with `Bash(jest:*) Bash(vitest:*) Bash(pytest:*)` for precision.
