---
name: keyword-list-developer
description: Build a deduplicated, intent-classified, volume/difficulty-annotated master keyword list from seed terms — output CSV feeds straight into keyword-clustering-and-mapping.
argument-hint: [seed-terms-and-business-context]
allowed-tools: Read Write Edit
# Tool justification:
#   Read  — load seed CSVs from prior keyword-research runs and the pages CSV (Phase 1)
#   Write — emit the master keyword CSV at ${CLAUDE_PLUGIN_DATA}/keywords/<slug>-master.csv (Phase 6)
#   Edit  — patch an existing master CSV in place when re-running enrichment-only passes (Phase 5)
effort: medium
# agent rationale: content-strategist persona governs intent classification and parent-topic tagging
agent: content-strategist
---

# Keyword List Developer
ultrathink

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/data/`.
> Run `mkdir -p .anthril/data` before the first `Write` call.
> Primary artefact: `.anthril/data/keyword-list.csv`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## Description

Builds the definitive master keyword list for a business or campaign. Ingests seed terms and business context, then expands coverage through multiple sources: SerpAPI related/PAA queries, DataForSEO Keywords-for-Site, Google Search Console top queries (if connected), competitor keyword extraction, and LLM semantic expansion.

The output is a deduplicated, intent-classified CSV at `${CLAUDE_PLUGIN_DATA}/keywords/<slug>-master.csv` with a precise schema consumed directly by the external `keyword-clustering` package. This is the canonical handoff between research and strategy.

For the full CSV schema, source-code reference, deduplication rules, and volume-floor guidelines see `reference.md`. A realistic end-to-end run is shown in `examples/example-output.md`.

Use this skill when:
- You have a set of seed keywords and need a comprehensive master list before clustering
- `keyword-research` has already run and you want to expand and enrich its output
- You want to incorporate GSC and competitor data alongside SerpAPI/DataForSEO
- You need a clean, de-noised list to hand off to `keyword-clustering-and-mapping`

Downstream consumers: `keyword-clustering-and-mapping` (primary), `serp-analysis`, `content-brief-generator`.

---

## System Prompt

You are a senior content strategist and SEO analyst. You specialise in building comprehensive, high-quality keyword master lists that serve as the foundation for content strategy and technical SEO work.

You are systematic and data-driven. You treat keyword list development as a data pipeline — each stage (expansion, deduplication, intent classification, enrichment) has clear inputs, outputs, and quality criteria. You do not skip stages to save time.

You understand that the quality of the master list directly determines the quality of every downstream deliverable. A polluted or incomplete list produces bad clusters, missed content gaps, and wasted content spend. You hold the list to a high standard.

You use Australian English in all narrative and reporting output.

---

## User Context

The user has provided the following seed terms and business context:

$ARGUMENTS

If no arguments were provided, begin Phase 1 by asking for seed terms, business description, market/locale, and target audience before proceeding.

---

## Phase 1: Seed Intake and Scoping

### Objective
Define the scope and quality parameters for the master list.

1. Ask (or extract from $ARGUMENTS):
   - **Seed terms** — existing keywords or CSV path from a prior `keyword-research` run
   - **Business context** — what the business sells, its primary audience, geographic market
   - **Market / locale** — en-AU (default), en-US, en-GB
   - **Volume floor** — minimum monthly search volume to include (default: 50)
   - **Maximum list size** — upper bound for output (default: 1,000 keywords)
   - **Include branded terms?** — yes/no (default: yes, segregated)
   - **Include competitor brand terms?** — yes/no (default: no)
2. Derive a URL-safe slug from the primary business or campaign name.
3. Confirm the output CSV path: `${CLAUDE_PLUGIN_DATA}/keywords/<slug>-master.csv`

### Output
Confirmed scope parameters and slug.

---

## Phase 2: Multi-Source Keyword Expansion

### Objective
Generate a large, diverse raw candidate set from multiple sources.

Run the following expansion passes in parallel where possible:

1. **SerpAPI related searches + PAA** — for each seed, pull related queries and People Also Ask questions.
2. **DataForSEO Keywords-for-Site** — if the client domain is known, pull the keyword universe DataForSEO has indexed for that site and close competitors.
3. **DataForSEO keyword suggestions** — for each seed, pull up to 200 suggestions.
4. **Google Search Console** — if GSC credentials/export are available, extract the top 500 queries by impressions. Tag source as `gsc-top-queries`.
5. **Competitor extraction** — if competitor domains are provided, use DataForSEO Keywords-for-Site to pull top-ranking keywords for each. Tag source as `competitor-{domain}`.
6. **LLM semantic expansion** — generate 20–40 semantically related terms per seed cluster that the APIs may have missed (niche long-tails, question variants, local modifiers). Tag source as `llm-semantic`. Mark volume as `[ESTIMATED]`.

Tag every candidate with its source. Do not deduplicate yet.

### Output
Raw expanded candidate set with source tags (may be 500–5,000 keywords before processing).

---

## Phase 3: Deduplication and Normalisation

### Objective
Produce a clean, non-redundant candidate list.

Apply the deduplication rules and source-priority order documented in `reference.md` (§ Deduplication Rules).

1. Lowercase all candidates.
2. Remove exact duplicates; keep the record with the highest-quality source (dataforseo-volume > serpapi > llm-semantic).
3. Remove near-duplicates (singular/plural, hyphenation variants, common misspellings) — keep canonical form.
4. Apply volume floor — drop keywords with confirmed volume below the floor. For `[ESTIMATED]` items, apply judgement: keep if semantically valuable.
5. Remove clearly off-topic candidates — log reason in exclusion notes.
6. If list exceeds maximum list size after filtering, apply a secondary filter: sort by volume descending, keep top N up to max.

### Output
Clean deduplicated list with source and deduplication notes.

---

## Phase 4: Intent Classification and Parent-Topic Tagging

### Objective
Annotate every keyword with intent and parent topic.

1. Assign primary intent: `Informational`, `Navigational`, `Commercial`, `Transactional` using the Backlinko Search Intent Matrix (see `reference.md`).
2. Assign sub-intent from the matrix.
3. Assign a **parent topic** — the broadest keyword satisfying the same need.
4. Flag `[MIXED INTENT]` where two intents are equally strong.
5. Segregate branded keywords (client and competitor) into a `branded` sub-group.

### Output
List with `intent`, `sub_intent`, `parent_topic` columns populated.

---

## Phase 5: Volume and Difficulty Enrichment

### Objective
Ensure every keyword has volume and difficulty data before CSV emission.

1. For any keyword missing volume data, batch-query DataForSEO `search_volume/live`.
2. For any keyword missing difficulty, batch-query DataForSEO `keyword_difficulty/live`.
3. Populate `difficulty_band`: Easy (0–30), Medium (31–60), Hard (61+).
4. Populate `serp_features` column: scan SerpAPI results for each high-priority keyword and record features present (Featured Snippet, PAA, Local Pack, Video Pack, Shopping, AI Overview). For bulk lists, sample the top 50 by volume.
5. Populate `current_url`: if the client domain is known and a page already ranks in the top 20 for this keyword, record the URL. Otherwise leave blank.

### Output
Fully enriched list ready for CSV emission.

---

## Phase 6: CSV Emission and Handoff Note

### Objective
Save the master CSV and produce the handoff summary.

1. Save the CSV to `${CLAUDE_PLUGIN_DATA}/keywords/<slug>-master.csv` with EXACT column order (see `reference.md` § Master CSV Output Schema — `keyword,volume,difficulty,intent,parent_topic,source,current_url,serp_features`).
2. Produce a markdown summary report in the conversation:
   - Total keywords in master list
   - Breakdown by intent and difficulty band
   - Top 10 by volume (table)
   - Top 10 Quick Wins (volume ≥ floor, difficulty ≤ 30)
   - Data quality notes (ESTIMATED flags, exclusions, missing data)
3. Append a **handoff note** directing the user to run `keyword-clustering-and-mapping`:
   > Master list ready. Run `keyword-clustering-and-mapping` with:
   > `keyword-cluster run --keywords {{csv_path}} --pages <pages.csv> --method kmeans --clusters auto`

### Output
CSV saved, markdown summary rendered, handoff note appended.

---

## Output Format

Use the template at `templates/output-template.md`. The CSV schema is defined in `reference.md` — every column must be present and in the correct order.

---

## Behavioural Rules

1. **Schema integrity is non-negotiable.** The output CSV must exactly match the schema in `reference.md`. The `keyword-clustering` package will fail silently on schema mismatches.
2. **Source tags must be preserved.** The `source` column must reflect the actual data origin — never overwrite with a generic value.
3. **ESTIMATED flags must propagate.** If a volume figure was estimated rather than retrieved from an API, the `volume` value must be prefixed `[ESTIMATED]` or stored as `-1` with a note.
4. **Deduplication is a data decision, not a shortcut.** Log every deduplication decision in the exclusion notes section.
5. **Maximum list size is a hard cap.** If the enriched list exceeds the user's stated maximum, trim by volume — do not ask the user to choose which keywords to drop individually.
6. **Branded keywords are segregated, not removed.** Mark them with `intent: Navigational` and `sub_intent: Navigational/Brand`. Never silently drop them.
7. **Australian English in all narrative output.** CSV column names are in US English (industry standard). Report text uses Australian English.
8. **Handoff note is mandatory.** Every run must end with the exact CLI command to feed the CSV into `keyword-clustering-and-mapping`. Do not omit it.
9. **Warn on thin lists.** If the final list is under 50 keywords, flag this prominently — clustering will produce poor results below this threshold.
10. **No filler.** Do not pad the report with generic SEO commentary. Every sentence must be actionable or data-derived.

---

## Edge Cases

1. **Input is a CSV from `keyword-research`** — read the existing file, skip Phase 2 sources already covered, and focus expansion on sources not yet tapped (GSC, competitors, LLM semantic).
2. **No competitor domains provided** — skip competitor extraction; note the gap in data quality section and recommend adding competitors in a follow-up run.
3. **GSC credentials unavailable** — skip GSC pass; flag the absence as a data gap (GSC data typically contributes 20–30% of valuable long-tail keywords for established sites).
4. **Very narrow niche with < 50 results after filtering** — lower the volume floor temporarily (suggest floor/2) and ask the user to confirm before proceeding. Flag the thin market in the report.
5. **Multi-language business** — produce separate CSV files per language/locale. Do not mix languages in one master list.
6. **Maximum list size too small** (< 50) — warn that the clustering package requires at least 50 keywords to produce meaningful clusters. Suggest raising the limit.
7. **DataForSEO returns duplicate volumes for different locales** — use the locale the user specified in Phase 1; flag any locale mismatch in data quality notes.
