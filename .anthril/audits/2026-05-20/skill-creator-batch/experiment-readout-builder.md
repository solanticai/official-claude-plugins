# Skill Audit — experiment-readout-builder

**Path:** `data-science/experimentation/skills/experiment-readout-builder/`
**Date:** 2026-05-20
**Files:** SKILL.md (139), templates/output-template.md (93), examples/example-output.md (118), LICENSE.txt. No reference.md — not needed at this size.

---

## Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| Discovery | 19 | 20 | Strong description front-loaded with key terms (SRM, CIs, decision matrix); argument-hint clear (`[results-data-or-csv]`). SKILL.md:2-6. Minor: could mention "A/B" earlier in name discovery surface. |
| Scope | 14 | 15 | Tight focus on readout production; pairs with ab-test-designer (referenced example-output.md:3). No scope drift into design or instrumentation. |
| Conciseness | 14 | 15 | 139 lines; phases are terse; behavioural rules condensed at SKILL.md:119-128. No fluff. |
| Architecture | 14 | 15 | 8 phases logically ordered: Validate → SRM → Primary → Secondary/Segment/Novelty → Guardrails → Decision → Peer Review → Follow-Ups. SRM gate at Phase 2 (SKILL.md:42-46) before any inference. |
| Content | 14 | 15 | Anti-p-hacking discipline (Edge Case 2, SKILL.md:134), no-swap rule (SKILL.md:122 rule 2), CI > p-value rule (SKILL.md:123). Example shows full novelty split + decision matrix verbatim application. |
| Tool | 9 | 10 | `allowed-tools: Read Write Edit Bash(python:*) Agent` (SKILL.md:5). Bash narrowed to python (good). Tool table at SKILL.md:91-99 maps each. Could add Glob for finding design doc. |
| Testing | 6 | 7 | One realistic example (118 lines) — fully populated with negative result + novelty pattern + reviewer findings. Could add a second example showing an SRM-failure stop. |
| Standards | 3 | 3 | YAML frontmatter complete; AusE present ("colour", "Analyse", "randomisation"); MIT license; effort: high appropriate. |
| Activation | 10 | 10 | Description starts with verb "Analyse A/B test results" + comma-list of distinguishing terms (significance, CIs, segment cuts, novelty/primacy, SRM, decision matrix, follow-up). 213 chars. |
| Anti-patterns | 5 | 5 | No metric-swap (rule 2), no p-hacking (edge case 2), no peeking (edge case 5), no stakeholder override (edge case 6). Explicit behavioural rules pre-empt the common failure modes. |
| **Total** | **108** | **115** | **Grade: A** |

---

## Special Checks

| Check | Result | Evidence |
|---|---|---|
| (a) SRM check first | PASS | Phase 2 is SRM, with hard stop on p<0.001 (SKILL.md:42-46). Output template Section 2 SRM precedes Primary Read (template:17-28). Rule 1 "SRM first. Always." (SKILL.md:121). |
| (b) Primary metric from design — no swaps | PASS | Phase 1 anchors pre-registration (SKILL.md:36). Rule 2 "Primary metric from design — no swaps." (SKILL.md:122). System prompt explicitly refuses retroactive change (SKILL.md:20-22). |
| (c) Agent tool for stats-reviewer | PASS | `Agent` in allowed-tools (SKILL.md:5). Phase 7 invokes `stats-reviewer` (SKILL.md:79-82). Tool table maps Agent → stats-reviewer (SKILL.md:97). |
| (d) Bash(python:*) for stats calcs | PASS | `Bash(python:*)` narrowed permission (SKILL.md:5). Tool table: "z-test, CI" (SKILL.md:96). |

All four special checks pass cleanly.

---

## Strengths

1. **SRM-first discipline is structurally enforced**, not just mentioned — it gates downstream phases (SKILL.md:44 "stop and flag").
2. **Decision matrix applied verbatim** rule (SKILL.md:125) prevents post-hoc reinterpretation; example demonstrates honest "don't ship +5%" call (example:86).
3. **Novelty/primacy as a first-class phase** (Phase 4) — most readouts skip this. Example shows declining effect interpretation (example:65-67).
4. **stats-reviewer peer review built in** (Phase 7) — independent agent invocation is the right architecture for stats validation, not inline self-check.
5. **CI > p-value rule** (SKILL.md:123) is the right epistemic posture; example consistently leads with CI (example:38).

---

## Top 3 Fixes (P0)

### P0-1: Add a second example for SRM failure
Only happy-path example exists. The SRM-stop edge case (SKILL.md:133) is the most consequential branch and has no exemplar. Add `examples/example-srm-failure.md` showing the stop, instrumentation investigation notes, and refusal to produce primary readout.

### P0-2: Specify the SRM threshold rationale and test choice in Phase 2
SKILL.md:44 hardcodes p<0.001 chi-square without justifying. Add one-line note: "Chi-square goodness-of-fit; threshold p<0.001 avoids false positives from repeated SRM checks across experiments." Prevents reviewers questioning the bound.

### P0-3: Make stats-reviewer agent contract explicit
SKILL.md:81 says "Invoke `stats-reviewer` agent" but doesn't specify the input contract (does it receive the in-progress readout? raw data?) or where its output appears in the template (template:83-86 is just a placeholder). Add a sub-bullet: "Pass the populated template through Phase 6; reviewer appends to Section 7." Reduces ambiguity for the Agent call.

---

## Minor Suggestions (P1)

- Add Glob to allowed-tools so the skill can locate the design doc by pattern (`**/ab-test-design*.md`) without prompting.
- Phase 3 lists p-value alongside CI — reaffirm the rule "report both, lead with CI" inline so future maintainers don't reorder.
- Edge Case 5 (Day-3 peek) could cross-link to a sequential-design follow-up skill if one exists in the experimentation plugin.
- Output template Section "Decision (Matrix Applied)" has `{{action}}` twice (template:77, 79) — first as the matrix output, second as recommended action; clarify the distinction (matrix-says vs human-recommended-action with rationale).

---

## Verdict

**Grade: A (108/115).** A model skill for experimentation: rigorous SRM gate, no metric swaps, CI-led reporting, decision matrix applied verbatim, novelty surfaced, peer review delegated to a specialist agent. The negative-result example is honest and shows the skill's character. Ship as is; the three P0s are polish, not blockers.
