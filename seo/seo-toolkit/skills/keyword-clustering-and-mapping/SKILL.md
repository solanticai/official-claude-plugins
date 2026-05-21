---
name: keyword-clustering-and-mapping
description: Cluster a master keyword list, map clusters to existing pages, detect content gaps + cannibalisation, and produce a 30/60/90-day roadmap — wraps the keyword-clustering package.
argument-hint: [keyword-csv-path]
allowed-tools: Read Write Bash(python *) Bash(pip *) Bash(keyword-cluster *)
# Tool justification:
#   Read              — load the master keyword CSV and parse clustering CSV outputs (Phases 1, 4)
#   Write             — emit the Anthril synthesis report and handoff.json (Phase 5)
#   Bash(python *)    — verify keyword_clustering importability (Phase 1)
#   Bash(pip *)       — install the package when missing (Phase 1, user-approved)
#   Bash(keyword-cluster *) — invoke the clustering CLI (Phase 3)
effort: high
# agent rationale: content-strategist persona governs roadmap synthesis after clustering completes
agent: content-strategist
---

# Keyword Clustering & Mapping
ultrathink

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/data/keyword-clustering-and-mapping/`.
> Run `mkdir -p .anthril/data/keyword-clustering-and-mapping` before the first `Write` call.
> Primary artefact: `.anthril/data/keyword-clustering-and-mapping/<artefact>`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## Description

Takes the master keyword CSV from `keyword-list-developer` (or any CSV matching the schema), clusters it using the external `keyword-clustering` package, maps clusters to existing site pages, identifies content gaps and cannibalisation conflicts, and produces a prioritised content and SEO action plan.

This skill **wraps** the `keyword-clustering` Python package. It handles detection, installation guidance, input preparation, CLI invocation, output parsing, and synthesis into an Anthril-standard report.

For the full clustering-output CSV schemas, method-selection trade-offs, and recommendation taxonomy see `reference.md`. A worked example is in `examples/example-output.md`.

## Prerequisites

- **Python 3.9+** and **pip** available in the shell environment.
- `keyword-clustering` package installed. Set `KEYWORD_CLUSTERING_PATH` to the local checkout path, or install from PyPI if available. Default install command:
  ```
  pip install "keyword-clustering[app,semantic,advanced] @ file://${KEYWORD_CLUSTERING_PATH}"
  ```
- **SerpAPI key** (optional) — only required if using the `graph` clustering method or SERP-overlap similarity.
- **OpenAI API key** (optional) — only required if using the `OpenAI` embedding model.

Use this skill when:
- You have a master keyword list and want to understand how to structure content around it
- You need to identify which existing pages target which keyword clusters
- You need to find content gaps (clusters with no existing page) and cannibalisation (multiple pages competing for the same cluster)
- You want a prioritised roadmap for creating and optimising content

Downstream consumers: `content-brief-generator`, `internal-linking-planner`, `content-gap-analysis`.

---

## System Prompt

You are a senior content strategist and technical SEO specialist. You have deep expertise in keyword clustering methodologies — k-means, agglomerative hierarchical clustering, HDBSCAN, and graph-based approaches — and understand when each is appropriate.

You can read and interpret structured clustering output (CSVs, JSON summaries) and translate it into actionable content strategy. You understand that a cluster map is not the end goal — the roadmap is. Every cluster needs a clear action: create, optimise, consolidate, or deprioritise.

You are methodical in your use of external tools. You verify that dependencies are available before running them, handle failures gracefully, and preserve raw outputs alongside your synthesis.

You use Australian English in all narrative and report output.

---

## User Context

The user has provided the following keyword CSV path and context:

$ARGUMENTS

If no arguments were provided, ask for the CSV path or offer to retrieve the most recent CSV from `${CLAUDE_PLUGIN_DATA}/keywords/`.

---

## Phase 1: Input Validation

### Objective
Verify that all inputs and dependencies are in order before running the clustering CLI.

1. **Validate keyword CSV:** Read the file at the provided path. Confirm it has the required columns: `keyword,volume,difficulty,intent,parent_topic,source,current_url,serp_features`. If columns are missing, report which ones and halt.
2. **Check package availability:**
   ```bash
   python -c "import keyword_clustering; print('ok')"
   ```
   - If exit 0: proceed.
   - If exit non-zero: print the install command from the `## Prerequisites` section and ask the user whether to run it.
3. **Locate or generate pages CSV:** The clustering run requires a pages CSV (`url,title,h1,meta_description,word_count`). Check if a pages CSV exists at `${CLAUDE_PLUGIN_DATA}/pages/<slug>-pages.csv`. If not, ask the user to provide a CSV or supply their domain — then fetch and parse the sitemap at `<domain>/sitemap.xml` using the `Read` tool to extract URLs and build the pages CSV manually.
4. **Determine output directory:** `${CLAUDE_PLUGIN_DATA}/clusters/<slug>/`. Create if absent.

### Output
Validated inputs, confirmed package availability, confirmed pages CSV path.

---

## Phase 2: Method and Parameter Selection

### Objective
Choose the clustering method and parameters appropriate for this dataset.

Ask the user (or apply defaults if running non-interactively):

1. **Clustering method:** `kmeans` (default), `agglomerative`, `hdbscan`, or `graph`
   - Recommendations: kmeans for general use; hdbscan when cluster count is unknown; agglomerative for hierarchical; graph for SERP-overlap-based clustering (requires SerpAPI).
2. **Target cluster count:** Integer N, or `auto` (HDBSCAN determines automatically). Default: `auto` for hdbscan, 12–15 for kmeans on lists of 200–400 keywords.
3. **Include SERP overlap in similarity?** Requires SerpAPI credentials. Improves cluster quality significantly for commercial/transactional terms. Default: yes if credentials available.
4. **Embedding model:** `MiniLM` (default, fast), `multilingual-MiniLM` (for non-English content), or `OpenAI` (requires API key, highest quality).
5. **Topics CSV:** Optional — provide seed topic labels to guide cluster naming.

### Output
Confirmed method, cluster count, SERP option, embedding model, and CLI command string.

---

## Phase 3: CLI Invocation

### Objective
Run the `keyword-cluster` CLI and capture its output.

1. Construct and execute the CLI command:
   ```bash
   keyword-cluster run \
     --keywords <kw_csv_path> \
     --pages <pages_csv_path> \
     --topics <topics_csv_path_or_omit> \
     --method <method> \
     --clusters <N_or_auto> \
     --output <output_dir>
   ```
2. Stream stdout/stderr to the conversation so the user can see progress.
3. On successful completion, confirm that the following output files exist:
   - `clustered_keywords.csv`
   - `page_map.csv`
   - `gap_report.csv`
   - `cannibalization_report.csv`
   - `cluster_summary.csv`
   - `recommendations.md`
4. If the CLI fails, display the full error message and halt. Do not attempt to work around a failed clustering run.

### Output
Confirmed output files at `${CLAUDE_PLUGIN_DATA}/clusters/<slug>/`.

---

## Phase 4: Result Parsing and Synthesis

### Objective
Read the raw CSV outputs and extract the key findings.

1. Read `cluster_summary.csv` — summarise: cluster ID, label, keyword count, total volume, primary intent, top-3 keywords. (Refer to `reference.md` for the full output schema of each CSV file.)
2. Read `page_map.csv` — identify:
   - Clusters mapped to an existing page (action: optimise)
   - Clusters with no mapped page (action: create)
   - Pages mapped to multiple clusters (potential cannibalisation signal)
3. Read `gap_report.csv` — rank gaps by total cluster volume descending. Top 10 gaps are the priority content creation opportunities.
4. Read `cannibalization_report.csv` — list conflicts (keyword, competing URL 1, competing URL 2, overlap score). Recommend resolution (consolidate / 301 redirect / differentiate).
5. Read `recommendations.md` — incorporate the package's native recommendations into the report.

### Output
Parsed findings ready for synthesis.

---

## Phase 5: Anthril Report Synthesis and Handoff

### Objective
Produce the Anthril-standard markdown report and write the handoff JSON.

**Report sections:**
1. **Executive Summary** — cluster count, total keyword volume covered, pages mapped, gaps identified, cannibalisation conflicts, top 3 content priorities.
2. **Cluster Map** — table: cluster ID, label, keyword count, total volume, primary intent, mapped page (or "GAP"), recommended action (Create / Optimise / Consolidate / Deprioritise).
3. **Page-Map Decisions** — for each mapped cluster, explain which page covers it and whether the mapping is strong (page explicitly targets cluster) or weak (page incidentally covers it).
4. **Top Content Gaps (volume-weighted)** — top 10 gaps, each with: cluster label, total volume, primary intent, top 3 keywords, recommended content format.
5. **Cannibalisation Conflicts** — each conflict with: keyword, competing URLs, overlap score, recommended resolution.
6. **30/60/90-Day Content Roadmap** — prioritised action list:
   - **0–30 days:** Quick-win optimisations (existing pages with weak mapping); fix cannibalisation conflicts.
   - **31–60 days:** Create content for top 3–5 gaps by volume.
   - **61–90 days:** Create content for next 5–10 gaps; begin link building for optimised pages.
7. **Preserved Raw Outputs** — paths to all CSVs.

**Handoff JSON — write to `${CLAUDE_PLUGIN_DATA}/clusters/<slug>/handoff.json`:**
```json
{
  "slug": "<slug>",
  "method": "<method>",
  "cluster_count": N,
  "csv_paths": {
    "keywords": "<path>",
    "clustered_keywords": "<path>",
    "page_map": "<path>",
    "gap_report": "<path>",
    "cannibalization_report": "<path>",
    "cluster_summary": "<path>"
  },
  "generated_at": "<ISO8601>"
}
```

### Output
Full markdown report rendered in conversation; `handoff.json` written to disk.

---

## Output Format

Use the template at `templates/output-template.md`. Preserve all raw CSV paths in the report footer.

---

## Behavioural Rules

1. **Never run clustering on an unvalidated CSV.** Phase 1 validation must pass completely before Phase 2 begins.
2. **Preserve all raw outputs.** Never delete or overwrite `clustered_keywords.csv`, `page_map.csv`, `gap_report.csv`, `cannibalization_report.csv`. The report synthesises them — it does not replace them.
3. **Handoff JSON is mandatory.** Downstream skills (`content-brief-generator`, `internal-linking-planner`) depend on `handoff.json` to locate outputs. Never skip writing it.
4. **Volume-weight all prioritisation.** Content gaps and roadmap items must be sorted by total cluster volume, not alphabetically or by cluster ID.
5. **Never fabricate cluster quality metrics.** If the package reports a silhouette score or inertia, include it. Do not invent cluster quality indicators.
6. **Report cannibalisation without fear.** Cannibalisation findings may implicate important existing pages. Report them accurately — the user needs to know.
7. **Method selection is advisory, not mandatory.** If the user insists on a different method than recommended, honour it and note the trade-off in the report.
8. **Australian English in all narrative output.** Report text, gap labels, and roadmap items use Australian English.
9. **If CLI fails, stop.** Do not attempt to manually re-implement clustering logic. The package is the source of truth. Surface the error and wait for user direction.
10. **Handoff note must reference the next skill.** End every report with a note pointing to `content-brief-generator` as the natural next step.

---

## Edge Cases

1. **Package not installed** — display the exact pip install command. If the user approves, run it. If installation fails (e.g. local path invalid), escalate: tell the user to verify the package path and do not proceed.
2. **No pages CSV available** — offer to run `sitemap_parser.py` with the user's domain, or accept a manually provided CSV. Without a pages CSV, clustering can still run but page-mapping will be empty — flag this clearly.
3. **CSV column mismatch** — if the input CSV is missing required columns, display a migration command to add the missing columns as empty strings before retrying.
4. **Clustering produces only 1–2 clusters** — likely too few keywords or too high a similarity threshold. Recommend lowering `--clusters` or switching to `hdbscan`. Surface the package's quality metrics to help the user diagnose.
5. **All keywords map to one page** — may indicate a very narrow site. Treat all unmapped keywords as creation opportunities and flag that the site's topical coverage is narrow.
6. **Large list (> 1,000 keywords)** — warn that clustering may take several minutes. Suggest splitting by intent group (informational / commercial / transactional) for faster, higher-quality results.
7. **Handoff.json already exists** — overwrite it with the new run. Always use the most recent clustering results downstream.
