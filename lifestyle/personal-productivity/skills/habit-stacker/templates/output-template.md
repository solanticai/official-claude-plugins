# Habit Stack — {{user_name_or_alias}}

**Date:** {{date_dd_mm_yyyy}}
**Identity:** {{identity_short_form}}
**Stack length:** {{n}} habits
**Prepared by:** Habit Stacker skill

---

## Identity Statement

> {{identity_paragraph}}

---

## The Stack

1. **After [{{anchor_1}}], I will [{{habit_1}}] at [{{location_1}}].**
   - Cue: {{cue_1}}
   - Reward: {{reward_1}}
   - Minimum-viable version: {{mv_1}}
2. **After [{{anchor_2}}], I will [{{habit_2}}] at [{{location_2}}].**
   - Cue: {{cue_2}}
   - Reward: {{reward_2}}
   - Minimum-viable version: {{mv_2}}
3. _Add more rows as needed (max 4)_

---

## Stack Flow

```mermaid
flowchart TD
  A[{{anchor_1}}] --> B[{{habit_1}}]
  B --> C[{{habit_2}}]
  C --> D[{{habit_3}}]
  D --> E[{{reward_end}}]
```

---

## Friction Design

| Habit | Remove from environment | Add to environment |
|-------|------------------------|--------------------|
| {{habit_1}} | {{remove}} | {{add}} |
| {{habit_2}} | {{remove}} | {{add}} |

---

## Tracker Spec

- **Format:** {{paper_grid_or_app_or_partner_text}}
- **Streak rule:** Never miss twice. One miss is recovery; two in a row means redesign.
- **Review cadence:**
  - End-of-day glance: 30 seconds
  - End-of-week review: 5 minutes (every {{day_of_week}})
  - End-of-month redesign: 15 minutes (last day of month)

---

## 8-Week Ramp

| Week | Focus | Intensity | Notes |
|------|-------|-----------|-------|
| 1–2 | {{week_1_2_focus}} | Minimum-viable only | Streak focus |
| 3–4 | {{week_3_4_focus}} | +25% on keystone | {{notes}} |
| 5–6 | {{week_5_6_focus}} | Layer in habit 2 & 3 | {{notes}} |
| 7–8 | {{week_7_8_focus}} | Full intensity | First monthly review at end of week 8 |

---

## Failure Modes & Recovery

| Failure mode | Likelihood | Symptom | Recovery move |
|--------------|-----------|---------|---------------|
| {{mode_1}} | {{high_med_low}} | {{symptom}} | {{recovery}} |
| {{mode_2}} | {{high_med_low}} | {{symptom}} | {{recovery}} |
| {{mode_3}} | {{high_med_low}} | {{symptom}} | {{recovery}} |
| {{mode_4}} | {{high_med_low}} | {{symptom}} | {{recovery}} |
| {{mode_5}} | {{high_med_low}} | {{symptom}} | {{recovery}} |

---

## First-Week Checklist

| Day | Trigger | Done? |
|-----|---------|-------|
| Mon | {{trigger}} | ☐ |
| Tue | {{trigger}} | ☐ |
| Wed | {{trigger}} | ☐ |
| Thu | {{trigger}} | ☐ |
| Fri | {{trigger}} | ☐ |
| Sat | {{trigger}} | ☐ |
| Sun | End-of-week review | ☐ |

---

## Next Steps

1. {{next_step_1}}
2. {{next_step_2}}
3. {{next_step_3}}
