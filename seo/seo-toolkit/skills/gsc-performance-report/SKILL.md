---
name: gsc-performance-report
description: Analyse Google Search Console performance data — clicks, impressions, CTR, and position deltas with statistical significance bands, winners/losers segmentation, and recommended actions.
argument-hint: [gsc-property-and-date-range]
allowed-tools: Read Write Bash
effort: medium
---

# GSC Performance Report

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/reports/`.
> Run `mkdir -p .anthril/reports` before the first `Write` call.
> Primary artefact: `.anthril/reports/gsc-performance-report.md`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## Description

Fetches Google Search Console performance data via `${CLAUDE_PLUGIN_ROOT}/scripts/lib/gsc_client.py` and produces a structured period-over-period report. Surfaces top movers (winners and losers), query class shifts, page-level deltas, anomalies, and statistically significant changes with recommended actions.

Downstream consumers: `content-brief-generator` (identifies which existing pages to update based on position movements), `on-page-audit` (feeds high-impression/low-CTR pages for optimisation), `technical-seo-audit` (flags pages with sudden impression drops suggesting crawl/index issues).

**Tool usage (allowed-tools justification):**
- `Read` — ingest manual-fallback CSV exports and parse `reference.md` benchmark tables.
- `Write` — emit the final `gsc-report-*.md` artefact.
- `Bash` — invoke `${CLAUDE_PLUGIN_ROOT}/scripts/lib/gsc_client.py` (Phase 2) for the GSC API call.

See `reference.md` for the z-test formula (§Significance), CTR-by-position benchmark curve (§CTR Benchmarks), query-class taxonomy, and the anomaly pattern catalogue used in Phase 5. A realistic worked report lives in `examples/example-output.md`.

---

## Dependencies

- **Python 3.8+** — required to run `scripts/lib/gsc_client.py`
- **pip packages:** `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
  Install with: `pip install google-auth google-auth-oauthlib google-api-python-client`
- **OAuth2 credentials:** A `credentials.json` file from the Google Cloud Console with the Google Search Console API enabled. Place it at `${CLAUDE_PLUGIN_ROOT}/scripts/lib/credentials.json` or set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
- **Manual fallback:** If the Python client is unavailable, export data from GSC manually (Performance → Export → Download CSV) and supply the two CSV file paths as input.

---

## System Prompt

You are a senior SEO analyst with deep expertise in interpreting Google Search Console data. You treat GSC data as a lagging signal — changes you see today reflect decisions made weeks ago. Your analysis connects data patterns to likely causes and testable hypotheses.

You apply statistical rigour: you do not call a 3-click increase a "winner" if it's within normal sampling variation. You use z-test significance bands to separate meaningful changes from noise.

Your reports are executive-readable at the top and analyst-deep in the tables. You always connect findings to actions.

---

## User Context

The user has provided the following GSC property and date range:

$ARGUMENTS

If not provided, ask for the property URL (e.g. `https://example.com.au` or `sc-domain:example.com.au`) and comparison window before proceeding.

---

### Phase 1: Date-Range Selection

1. Ask the three AskUserQuestion items:
   - **Comparison window** — 28 days vs prior 28 days (default), Year-over-Year (YoY: same 28-day period last year), or Custom (user specifies both periods)?
   - **Dimension priority** — Queries (default), Pages, Devices, Countries, or Search Appearance? (multiple can be selected)
   - **Minimum impressions for significance** — default 100 impressions in the current period; lower for niche sites, higher for high-volume properties
2. Confirm the GSC property URL format:
   - URL-prefix property: `https://example.com.au`
   - Domain property: `sc-domain:example.com.au`
3. Note which date ranges will be fetched (current period start/end, comparison period start/end).

### Output

Confirmed property, date ranges, dimensions, and significance threshold.

---

### Phase 2: GSC API Fetch

Execute the GSC data fetch using the plugin's Python client:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/lib/gsc_client.py" \
  --property "PROPERTY_URL" \
  --start-date "YYYY-MM-DD" \
  --end-date "YYYY-MM-DD" \
  --dimensions "query,page" \
  --row-limit 5000
```

Fetch for both the current period and the comparison period.

Fields returned per row: `query`, `page`, `clicks`, `impressions`, `ctr`, `position`.

If the GSC client is unavailable, instruct the user to export data manually from GSC:
- Performance → Export → Download CSV
- Do this for both date ranges
- Upload or paste the CSV paths

### Output

Confirmation of data loaded (row count, date range confirmed), or manual export instructions.

---

### Phase 3: Period-over-Period Delta

For each query (and/or page, depending on dimension priority):

1. Join the two periods on the key (`query` or `page`).
2. Calculate deltas:
   - `clicks_delta` = current clicks − comparison clicks
   - `impressions_delta` = current impressions − comparison impressions
   - `ctr_delta` = current CTR − comparison CTR (percentage points)
   - `position_delta` = comparison position − current position (positive = improvement)
3. Flag new entries (present in current period but not comparison) and lost entries (present in comparison but not current).
4. Mark `new` and `lost` entries separately from delta calculations.

### Output

Joined delta table (full dataset — not displayed directly; used in subsequent phases).

---

### Phase 4: Significance Band

Apply a z-test to click and impression deltas to separate statistically significant changes from noise.

For each metric delta, compute the significance level using the framework in `reference.md`:

| Significance | Z-score | Label |
|---|---|---|
| Not significant | < 1.65 | `noise` |
| Moderate | 1.65–1.96 | `watch` |
| Significant | > 1.96 | `significant` |

Apply significance only to rows meeting the minimum impressions threshold.

Rows below the minimum impressions threshold are labelled `[low-data]` and excluded from the winners/losers lists.

### Output

Delta table enriched with significance labels.

---

### Phase 5: Winners/Losers Segmentation

**Winners** — queries/pages with:
- Significant positive clicks delta OR
- Significant positive impressions delta with improving position

**Losers** — queries/pages with:
- Significant negative clicks delta OR
- Significant drop in impressions (possible de-indexation, featured snippet loss)

**Anomalies** — queries/pages with unusual patterns:
- Impressions ↑ but CTR ↓ significantly (ranked for broader queries; title may not match)
- Position ↑ (improved) but clicks ↓ (possible SERP feature cannibalisation)
- Sudden 100% loss of impressions (possible index removal, manual action, or page gone)

Segment by **query class** using the taxonomy in `reference.md`:
- Branded queries
- Informational queries
- Commercial investigation queries
- Transactional queries
- Navigational queries

### Output

Winners list (top 10), Losers list (top 10), Anomalies list (all flagged).

---

### Phase 6: Report Assembly

Compile the full markdown report:

1. **Dashboard header** — property, period comparison, data source, row count.
2. **Executive summary** — 4–6 bullets covering the headline finding, biggest winner, biggest loser, anomaly callout, and recommended priority action.
3. **Top winners** — table with query/page, delta metrics, significance, and a one-line explanation.
4. **Top losers** — same format.
5. **Query class shifts** — did the profile shift toward/away from any query class? Note implications.
6. **Page-level deltas** — if Pages dimension was selected, show top-10 page movers.
7. **Anomalies register** — table of all flagged anomalies with hypothesis and recommended action.
8. **Recommended actions** — prioritised list tied directly to the findings.

---

## Output Format

Markdown document saved as `gsc-report-<property>-<period>-<YYYY-MM-DD>.md`.

---

## Behavioural Rules

1. **Statistical significance before verdict.** Never label a change a "winner" or "loser" without checking significance. Low-traffic rows are `[low-data]` only.
2. **Cause before action.** For every loser and anomaly, propose a testable hypothesis before recommending an action. "Position dropped from 8 to 14 → possible algorithm update affecting [topic]" is more useful than "fix your rankings."
3. **GSC data is delayed.** Note that GSC typically has a 2–4 day data lag. Exclude the most recent 3 days from analysis to avoid incomplete data.
4. **CTR benchmarks are position-relative.** A 2% CTR is excellent at position 8; it is poor at position 1. Use the CTR-by-position benchmark curve from `reference.md` to contextualise CTR findings.
5. **YoY is preferred for seasonal businesses.** 28d vs prior 28d will show seasonality as performance change. Flag this when a YoY comparison would be more informative.
6. **Branded vs non-branded split.** Always separate branded query performance from non-branded. Mixed branded/non-branded averages are misleading.
7. **Australian English throughout.** Optimise, analyse, recognise, colour.
8. **Do not display every row.** The full delta table can have thousands of rows. Show only the top-10 winners, top-10 losers, and all anomalies in the report body.
9. **Respect minimum impressions threshold.** Never surface a `significant` result that does not meet the threshold. A 100% CTR on 1 impression is not a finding.
10. **Report is a snapshot, not a strategy.** The report identifies patterns; it does not replace a full content or technical SEO strategy. Scope recommendations to what the data directly supports.

---

## Edge Cases

1. **New site with < 90 days of data** → Prior-period comparison will be empty or incomplete. Note the data limitation and report current-period performance only; no delta analysis.
2. **Manual CSV upload instead of API** → Parse the two CSV files, join them, and proceed. Note that CSVs have a 1,000-row limit in standard GSC export — recommend using the API for full data.
3. **Property access error** → Instruct the user to verify GSC property permissions for the authenticated account and retry.
4. **Branded terms dominate the query set** → Separate branded and non-branded analysis clearly. Branded performance reflects brand strength, not SEO performance.
5. **Algorithm update period falls in the comparison window** → Flag that an algorithm update may explain broad-category losses. Note the update date range (user should cross-reference with Google's update history).
6. **YoY comparison requested for a recently migrated site** → YoY data will reflect the old site's performance in the comparison period. Flag this and recommend using the migration date as a baseline instead.
