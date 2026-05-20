# Keyword Research — {{product_or_service}}

**Domain:** {{domain}}
**Seeds used:** {{seed_count}}
**Expanded total:** {{expanded_count}}
**Clusters:** {{cluster_count}}
**Date:** {{DD_MM_YYYY}}

---

## Clusters (proposed ad groups)

{{#clusters}}
### {{theme}} ({{keyword_count}} keywords)

| Keyword | Match type | Est. avg monthly searches | Est. CPC (AUD) | Intent |
|---|---|---|---|---|
{{#keywords}}
| {{text}} | {{match_type}} | {{volume}} | {{cpc}} | {{intent}} |
{{/keywords}}

{{/clusters}}

---

## Negative keyword candidates

| Keyword | Match type | Rationale |
|---|---|---|
{{#negatives}}
| {{text}} | {{match_type}} | {{rationale}} |
{{/negatives}}

---

## CSV exports

- `keyword_research_{{date}}.csv` — full list with columns `Campaign, Ad Group, Keyword, Match Type, Default CPC, Final URL`
- `negative_keywords_{{date}}.csv` — negative list

Paste into Google Ads Editor → Import → From file.

---

## Next steps

1. Review the clusters — merge, split, or rename as needed.
2. Run `/ppc-manager:google-search-campaign` with the final keyword list.
3. Install the negative keyword list as a shared library list.
