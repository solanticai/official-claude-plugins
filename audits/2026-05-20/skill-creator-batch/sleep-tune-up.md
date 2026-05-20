# Skill Audit — sleep-tune-up

Path: `lifestyle/health-wellness/skills/sleep-tune-up`
Date: 2026-05-20

## Special checks

- (a) Disclaimer at top of template: YES — `templates/output-template.md:3` (blockquote "Disclaimer — read first").
- (b) Red-flag referral pattern clear in Phase 1: YES — `SKILL.md:49-51` lists snoring/apnoea, chronic insomnia > 3 months, shift work, low mood and routes to GP/sleep physician before any protocol.
- (c) AskUserQuestion in allowed-tools: NO — `SKILL.md:5` lists only `Read Write Edit`. Phase 1 ("If no log, ask Phase 1 questions" `SKILL.md:38`) expects multi-turn intake, so AskUserQuestion would be a natural fit. Minor gap.

## Scores

### 1. Discovery — 18 / 20
- `description` (`SKILL.md:3`) is 152 chars, front-loaded with audit/prescribe/re-measure — strong.
- "Use this skill when" bullets (`SKILL.md:15-20`) give clear triggers.
- `argument-hint: [sleep-log-or-narrative]` (`SKILL.md:4`) is specific.
- Minor: trigger list is symptom-focused; could add lifestyle triggers ("shift work", "new baby") to widen discovery.

### 2. Scope — 14 / 15
- Tight scope: audit + 14-day protocol + re-measurement. Does not stray into clinical territory.
- Edge cases (`SKILL.md:132-139`) explicitly defer shift work, apnoea, alcohol dependence — good boundary discipline.
- Slight overlap risk with a CBT-I or chronotype skill, but referenced (Walker, AASM, CBT-I) rather than re-implemented.

### 3. Conciseness — 14 / 15
- 140 lines, well under 500.
- No dense reference material that warrants extraction; absence of `reference.md` is appropriate.
- Phases are crisp; only minor redundancy between Phase 3 (`SKILL.md:70-77`) and Output Format bullets (`SKILL.md:108-114`).

### 4. Architecture — 12 / 15
- Clean phase structure (Intake → Lever → Protocol → Re-measure).
- Templates + examples present. No `reference.md` and not needed — caffeine half-life, temperature targets, dB threshold are inline (`SKILL.md:74`, template:48-52).
- Gap: no scripts/ for optional sleep-log parsing despite `Read` tool and `[sleep-log-or-narrative]` argument hint.
- Phase headings use `###` (`SKILL.md:42, 55, 68, 81`) whereas convention is `##` for top-level phases — minor inconsistency.

### 5. Content quality — 14 / 15
- Behavioural rules (`SKILL.md:120-128`) are evidence-aligned (caffeine half-life ~5h, chronotype respect, bedroom-for-sleep-and-sex).
- Edge cases substantive — jetlag pre-shift schedule, wearable trust calibration, alcohol-as-primary-cause flag.
- Example output (`examples/example-output.md`) is realistic: specific dosages (70mg/35mg caffeine residual at line 25), concrete schedule, dog displacement detail.
- Australian English consistent (colour/optimise n/a here; "honour" `SKILL.md:128`, "bedroom" usage; AEST/AEDT noted `SKILL.md:30`).
- Minor: success threshold "≥ 25% on ≥ 2 metrics" (`template:71`) lacks rationale; could cite minimum clinically important difference.

### 6. Tool usage — 7 / 10
- `allowed-tools: Read Write Edit` (`SKILL.md:5`) is minimal.
- Missing **AskUserQuestion** — Phase 1 explicitly asks 6 categories of questions if no log (`SKILL.md:44-50`); without AskUserQuestion the skill will use unstructured prose Q&A.
- Tool Usage table (`SKILL.md:96-100`) is honest but thin.

### 7. Testing — 5 / 7
- One example (`examples/example-output.md`) covers a realistic late-caffeine + email-arousal case.
- No example for a red-flag referral case (e.g. suspected apnoea) — would demonstrate the Phase 1 triage path.
- No example for shift-worker or parent-of-young-children edge cases despite explicit treatment in `SKILL.md:134-135`.

### 8. Standards compliance — 3 / 3
- Frontmatter valid; `effort: medium` appropriate.
- `LICENSE.txt` present.
- Australian English; markdown-first output.

### 9. Activation — 9 / 10
- Description front-loaded with use case (`SKILL.md:3`).
- "Use this skill when" list (`SKILL.md:15-20`) is concrete and symptom-anchored.
- argument-hint clear.
- Could add `paths:` glob for `*sleep*log*.md` to auto-suggest on log files.

### 10. Anti-patterns — 5 / 5
- No medical-diagnosis overreach.
- Disclaimer present in BOTH SKILL.md (`:22`) and template (`:3`).
- Refers out on red flags explicitly (`SKILL.md:51, 127, 138`).
- Doesn't promise specific outcomes — uses thresholds (≥25%) and contingent next steps.

## Total: 101 / 115 — Grade B

## Top 3 fixes (P0)

1. **Add `AskUserQuestion` to `allowed-tools`** (`SKILL.md:5`). Phase 1 (`SKILL.md:38, 44-50`) requires structured intake across 6 categories when no log is provided; without AskUserQuestion the skill defaults to free-text questioning, which produces inconsistent triage and risks missing a red flag (apnoea, chronic insomnia, low mood).

2. **Add a red-flag referral example** in `examples/` (companion to `example-output.md`). Currently the only example is a benign caffeine + screens case; a second example showing the skill correctly stopping at Phase 1 and writing a GP-referral plan (suspected apnoea: loud snoring + observed pauses + daytime sleepiness) would document the most safety-critical path the skill claims to handle (`SKILL.md:49-51, 127, 138`).

3. **Normalise phase headings to `##`** (`SKILL.md:42, 55, 68, 81` currently use `###`). The project convention in `.claude/CLAUDE.md` shows phases as `## Phase N: Title`. Minor but trips automated phase-extraction tooling and breaks consistency with sibling skills in `lifestyle/health-wellness`.

## Notes

- No `reference.md` — correct call, content is not dense enough to extract.
- Strong safety posture overall; the gap is operational (intake tooling + referral example), not clinical framing.
