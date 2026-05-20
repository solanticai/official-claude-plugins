# Energy Detective — Reference Material

## Energy Log CSV Schema

### Full schema (recommended)

```csv
date,hour,energy,focus,mood,context,notes
2026-05-06,07:00,2,2,3,"waking + coffee","slept 6h"
2026-05-06,09:00,4,4,4,"deep work — strategy doc","quiet office, headphones"
2026-05-06,13:00,2,2,3,"post-lunch + desk meeting","heavy carbs, fluorescent room"
```

Fields:

- `date` — ISO 8601 (YYYY-MM-DD)
- `hour` — HH:MM (24-hour)
- `energy` — 1 (depleted) to 5 (peak)
- `focus` — 1 (scattered) to 5 (locked-in)
- `mood` — 1 (low) to 5 (elevated)
- `context` — free-text — what was happening
- `notes` — free-text — anything else (food, people, weather)

### Minimal schema (4-bin daily)

If hourly is too much, log 4 bins per day:

```csv
date,bin,energy,context
2026-05-06,morning,4,"deep work"
2026-05-06,midday,3,"lunch + meetings"
2026-05-06,afternoon,2,"crashed"
2026-05-06,evening,3,"family + walk"
```

Minimal is fine for a first pass — but full hourly catches the ultradian pattern.

---

## Chronotype Heuristics

| Chronotype | Peak window | Typical dip | Signature |
|-----------|-------------|------------|-----------|
| Lark | 6–10am | 1–3pm | Wakes naturally before alarm; cognitively sharp before others arrive |
| Hummingbird (typical) | 9–11:30am | 2–4pm | Standard 9-to-5 fits; second wind 4–6pm |
| Owl | 12–4pm | morning | Slow start; productive afternoon and evening |
| Late-owl | 4pm–midnight | morning + early afternoon | Best work after 6pm; often artists, programmers, founders |
| Split | 9–11am + 7–10pm | midday + 3–5pm | Bimodal — needs two protected windows per day |

### How to classify from a log

1. Find the highest-energy continuous 3-hour window most days.
2. If that window is 6–10am most days → lark.
3. If 9–noon → hummingbird.
4. If 12–4pm → owl.
5. If 4pm+ → late-owl.
6. If two distinct peaks → split.

Variance is normal. Aim for the *dominant* pattern across 5+ days.

---

## Common Drain Patterns

| Drain category | Pattern in log | Action |
|---------------|---------------|--------|
| **Meeting-type drain** | Same meeting on calendar correlates with low-energy bin afterward | Move the meeting to a steady bin; change format (walk-and-talk; async; shorter) |
| **Post-meal crash** | 1–3pm bin consistently low | Lighter lunch; lunch away from desk; brief walk before returning |
| **Open-plan ambient drain** | Energy drops mid-afternoon in office days, not WFH days | Use headphones, find a quiet room, or shift deep work to WFH days |
| **Decision-fatigue drain** | Late-afternoon energy crashes faster than mornings | Eliminate trivial recurring decisions (pre-set lunch, outfit, first task) |
| **People-specific drain** | A specific person's meetings correlate with mood drop | Examine why; consider format change, fewer 1:1s, or boundary conversation |
| **Sleep-debt drain** | Energy floor is low across all bins, not just afternoon | Sleep audit — see [[sleep-tune-up]] |
| **Late-screen drain** | Energy in the bin *after* late screens drops next morning | Phone out of bedroom; lights down 60 min before bed |
| **Sugar/caffeine drain** | Sharp peak → sharp crash within 2 bins | Audit caffeine and sugar timing |

---

## Sample Interpretation Patterns

### Case 1 — "I'm just tired all the time"

Log shows: energy 2–3 across all bins, all days. No peak window.

**Likely root cause:** chronic sleep debt or something medical. Recommend GP visit before scheduling changes. Sleep-tune-up may help; do not assume scheduling fixes this.

### Case 2 — "I crash at 3pm every day"

Log shows: clear 1–3pm trough; recovery by 4. Mornings strong.

**Likely root cause:** normal afternoon dip + meal load. Move deep work out of the dip window. Lunch lighter and away from desk. Optional 15-min nap if available. The dip is biology — design around it, don't fight it.

### Case 3 — "Mondays are awful, Fridays are great"

Log shows: Monday morning low; Friday afternoon high.

**Likely root cause:** weekend rhythm break + Monday meeting load. Move major decisions off Mondays; cluster Friday afternoons for shipping easier work, not strategic ones.

### Case 4 — "I can't tell if I'm a morning or night person"

Log shows: bimodal — two peaks (9–11 and 7–9pm), trough at 2–5pm.

**Likely chronotype:** split. Design for two protected windows. The 2–5pm trough is the *off-duty* time — walk, exercise, errands, low-cognitive work. Do not try to "push through" the trough.

### Case 5 — "Saturdays are weirdly amazing"

Log shows: Saturday far higher than weekday averages.

**Likely root cause:** absence of obligations + natural rhythm. The signal is: weekday scheduling has more friction than the user realises. Audit which weekday inputs are absent on Saturday and try removing them one at a time during the work week.
