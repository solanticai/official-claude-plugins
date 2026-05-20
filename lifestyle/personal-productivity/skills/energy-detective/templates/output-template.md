# Energy Map — {{user_name_or_alias}}

**Log period:** {{start_dd_mm}} – {{end_dd_mm_yyyy}}
**Days logged:** {{n}}
**Prepared by:** Energy Detective skill

---

## Energy Heatmap

Scale: 1 (depleted) – 5 (peak). `—` = not logged.

| Day | 6am | 7 | 8 | 9 | 10 | 11 | 12 | 1pm | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10pm |
|-----|-----|---|---|---|----|----|----|-----|---|---|---|---|---|---|---|---|------|
| Mon | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} | {{v}} |
| Tue | … | | | | | | | | | | | | | | | | |
| Wed | … | | | | | | | | | | | | | | | | |
| Thu | … | | | | | | | | | | | | | | | | |
| Fri | … | | | | | | | | | | | | | | | | |
| Sat | … | | | | | | | | | | | | | | | | |
| Sun | … | | | | | | | | | | | | | | | | |

---

## Dominant Pattern

```mermaid
flowchart LR
  A[6–9am: {{state}}] --> B[9–12: {{state}}]
  B --> C[12–2pm: {{state}}]
  C --> D[2–4pm: {{dip_state}}]
  D --> E[4–6pm: {{state}}]
  E --> F[6–9pm: {{state}}]
```

---

## Top 3 Drains

| # | Drain | Frequency | Evidence |
|---|-------|-----------|----------|
| 1 | {{drain_1}} | {{n}}× | {{quote_or_pattern}} |
| 2 | {{drain_2}} | {{n}}× | {{quote_or_pattern}} |
| 3 | {{drain_3}} | {{n}}× | {{quote_or_pattern}} |

---

## Top 3 Restores

| # | Restore | Frequency | Evidence |
|---|---------|-----------|----------|
| 1 | {{restore_1}} | {{n}}× | {{quote_or_pattern}} |
| 2 | {{restore_2}} | {{n}}× | {{quote_or_pattern}} |
| 3 | {{restore_3}} | {{n}}× | {{quote_or_pattern}} |

---

## Chronotype & Cycle Map

- **Chronotype:** {{lark_hummingbird_owl_late_owl_split}}
- **Peak window:** {{peak_window}}
- **Afternoon dip:** {{dip_window}}
- **Ultradian rhythm:** ~{{cycle_minutes}}-min cycles; trough markers — {{markers}}

---

## One-Week Schedule Recommendation

| Slot | Energy state | Use for |
|------|-------------|---------|
| {{peak_slot}} | Peak | Deep work — protect via [[deep-focus-day]] |
| {{mid_slot}} | Steady | Meetings, 1:1s, planning |
| {{dip_slot}} | Trough | Admin, walks, light comms; not deep work |
| {{restore_slot}} | Restore | Walk, social, music — protect |

**Drains to remove/move next week:**

- {{drain_action_1}}
- {{drain_action_2}}

---

## 2 Hypotheses to Test (next 2 weeks)

1. **{{hypothesis_1}}** — success metric: {{metric_1}}
2. **{{hypothesis_2}}** — success metric: {{metric_2}}

---

## 5-Day Re-Log Template

Log only the changed bins to validate hypotheses.

| Day | Bin to log | Time | Energy (1–5) | Focus (1–5) | Notes |
|-----|-----------|------|-------------|-------------|-------|
| 1 | {{bin}} | {{t}} | | | |
| 2 | {{bin}} | {{t}} | | | |
| 3 | {{bin}} | {{t}} | | | |
| 4 | {{bin}} | {{t}} | | | |
| 5 | {{bin}} | {{t}} | | | |
