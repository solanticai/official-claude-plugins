---
name: lifestyle-onboard
description: Interactive lifestyle-onboard wizard — runs energy-detective → habit-stacker → deep-focus-day → sunday-reset in sequence with consolidated output
argument-hint: [--quick | --full]
---

# Lifestyle Onboard

This command walks the user through a complete personal-productivity setup by invoking the four skills in this plugin in sequence, with brief consolidation between each step.

## Modes

- `--quick` (default) — minimum-viable run. Each sub-skill uses its express / minimum form. ~25 minutes total.
- `--full` — full intake on every skill. ~60–90 minutes total.

## Flow

1. **Welcome message** — explain what's about to happen. Confirm the user has 25 / 60 minutes available right now.
2. **Energy Detective** — invoke `/personal-productivity:energy-detective`.
   - If the user has no log, accept narrative answers to: "best 2 moments and worst 2 moments of last week, with times".
   - In `--quick` mode, skip the full heatmap; produce a 3-line summary: peak window, dip window, primary drain.
3. **Habit Stacker** — invoke `/personal-productivity:habit-stacker`, passing the peak window from step 2 as preferred slot.
   - In `--quick` mode, cap the stack at 2 habits.
4. **Deep Focus Day** — invoke `/personal-productivity:deep-focus-day`, passing the peak window from step 2.
   - In `--quick` mode, produce only the day-of-week + Block 1 timing.
5. **Sunday Reset** — invoke `/personal-productivity:sunday-reset`.
   - In `--quick` mode, output the **express version** template only.
6. **Consolidated one-pager** — produce `lifestyle-plan.md` in the current directory, combining:
   - Peak window + dip window
   - Habit stack (2–4 habits with anchors)
   - Deep focus day (day + block 1 time + auto-reply script)
   - Sunday reset express template
   - **Three commitments the user is making this week** (extracted from the above)

## Behavioural Rules

- **Always confirm the time budget upfront.** Do not start a 60-minute flow with a user who has 10 minutes.
- **Pass context forward.** Energy peak from step 2 must inform steps 3 & 4. Do not re-ask.
- **End with three commitments.** Not seven, not the whole plan — three. The user should be able to remember them by heart at the end.
- **Save artefacts individually.** Each sub-skill saves its own `*.md` plus the consolidated `lifestyle-plan.md`.
- **Australian English throughout.**

## Error Handling

- **User runs out of time mid-flow** — save what's been produced so far; provide a one-line resume command (e.g. `/personal-productivity:deep-focus-day` to pick up at step 4).
- **Sub-skill fails or produces nothing usable** — continue with the next sub-skill; surface the gap in the consolidated one-pager so the user knows what's missing.
- **No context provided at all** — switch to `--quick` mode automatically and use the most common defaults (hummingbird chronotype, Wed deep-focus day, Sun evening reset).

## Final Message

After the consolidated `lifestyle-plan.md` is written, print:

> *Your lifestyle plan is saved to `lifestyle-plan.md`. Pin it somewhere visible. Your three commitments for this week:*
> *1. {commitment_1}*
> *2. {commitment_2}*
> *3. {commitment_3}*
> *Run `/personal-productivity:sunday-reset` next Sunday to review.*
