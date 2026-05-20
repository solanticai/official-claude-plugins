# Keyword Research — Wool Throws for Koala & Co.

**Domain:** koalahomewares.com.au
**Seeds used:** 10
**Expanded total:** 142
**Clusters:** 5
**Date:** 11/04/2026

---

## Clusters (proposed ad groups)

### Wool throw core (22 keywords)

| Keyword | Match type | Est. avg monthly searches | Est. CPC (AUD) | Intent |
|---|---|---|---|---|
| wool throw | Phrase | 4,400 | 1.20 | Purchase |
| wool throw blanket | Phrase | 2,900 | 1.40 | Purchase |
| [wool throw australia] | Exact | 890 | 1.60 | Purchase |
| wool throw for couch | Phrase | 720 | 1.10 | Purchase |
| wool throw sofa | Phrase | 480 | 1.00 | Purchase |
| wool throw bed | Phrase | 390 | 1.10 | Purchase |
| woollen throw | Phrase | 590 | 1.30 | Purchase |
| 100% wool throw | Phrase | 410 | 1.50 | Purchase |
| merino wool throw | Phrase | 1,800 | 1.80 | Purchase |
| [merino throw] | Exact | 620 | 1.70 | Purchase |
| ... (12 more) | | | | |

### Natural fibre throws (19 keywords)

| Keyword | Match type | Est. avg monthly searches | Est. CPC (AUD) | Intent |
|---|---|---|---|---|
| linen throw | Phrase | 2,400 | 1.30 | Purchase |
| linen throw blanket | Phrase | 1,700 | 1.50 | Purchase |
| cotton throw | Phrase | 1,100 | 1.00 | Purchase |
| natural throw blanket | Phrase | 590 | 1.20 | Purchase |
| organic throw | Phrase | 480 | 1.40 | Purchase |
| ... (14 more) | | | | |

### Handmade / Australian-made (16 keywords)

| Keyword | Match type | Est. avg monthly searches | Est. CPC (AUD) | Intent |
|---|---|---|---|---|
| handmade throw blanket | Phrase | 980 | 1.50 | Purchase |
| australian made throw | Phrase | 720 | 1.70 | Purchase |
| [aussie made wool throw] | Exact | 180 | 1.80 | Purchase |
| artisan throw | Phrase | 210 | 1.40 | Purchase |
| small batch throw | Phrase | 90 | 1.30 | Purchase |
| ... (11 more) | | | | |

### Seasonal / occasion (14 keywords)

| Keyword | Match type | Est. avg monthly searches | Est. CPC (AUD) | Intent |
|---|---|---|---|---|
| winter throw | Phrase | 2,100 | 1.00 | Purchase |
| cosy winter throw | Phrase | 480 | 1.10 | Purchase |
| warm blanket | Phrase | 6,200 | 0.80 | Mixed (some non-intent) |
| heavy throw | Phrase | 720 | 1.00 | Purchase |
| ... (10 more) | | | | |

### Brand & competitor defensive (8 keywords)

| Keyword | Match type | Est. avg monthly searches | Est. CPC (AUD) | Intent |
|---|---|---|---|---|
| [koala throws] | Exact | 390 | 0.90 | Brand |
| [koala and co throws] | Exact | 170 | 0.90 | Brand |
| koala homewares | Phrase | 290 | 1.00 | Brand |
| ... (5 more) | | | | |

---

## Negative keyword candidates

| Keyword | Match type | Rationale |
|---|---|---|
| free | Broad | Price-sensitive junk |
| cheap | Broad | Contradicts premium positioning |
| cheapest | Broad | Same |
| diy | Broad | Informational / DIY |
| how to | Broad | Informational |
| tutorial | Broad | Informational |
| wholesale | Broad | B2B, not target |
| pet bed | Phrase | Koala doesn't sell pet beds |
| dog blanket | Phrase | Not target |
| adairs | Phrase | Competitor |
| pillow talk | Phrase | Competitor |
| bed bath n table | Phrase | Competitor |
| kmart | Phrase | Competitor / downmarket |
| target | Phrase | Competitor / downmarket |
| harvey norman | Phrase | Competitor |
| facebook marketplace | Broad | Junk |
| gumtree | Broad | Junk |
| craigslist | Broad | Junk |

Total: 18 negatives (with 5 canonical generic negatives shared across every campaign).

---

## CSV exports

- `keyword_research_koala_2026-04-11.csv` — 79 keywords across 5 ad groups
- `negative_keywords_koala_2026-04-11.csv` — 18 negatives

---

## Next steps

1. Review clusters with marketing team — specifically the "Seasonal / occasion" cluster has a high-volume "warm blanket" keyword that may have mixed intent. Consider removing or reclassifying.
2. Run `/ppc-manager:google-search-campaign` passing these 5 clusters as ad group structure.
3. Install the 18 negatives as the shared list `Koala - Core Negatives`.
4. Monitor for 7 days, then run `/ppc-manager:campaign-audit` to find additional negatives from real search terms.
