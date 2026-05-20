# Meta Audiences — {{ad_account_name}}

**Ad account:** {{ad_account_id}}
**Pixel:** {{pixel_id}}
**Date:** {{DD_MM_YYYY}}

---

## Retargeting audiences

| Name | Source event | Retention | Approx size | Status |
|---|---|---|---|---|
{{#retargeting}}
| {{name}} | {{source}} | {{retention}} | {{size}} | {{status}} |
{{/retargeting}}

---

## Lookalike audiences

| Name | Source audience | Country | Ratio | Approx size | Status |
|---|---|---|---|---|---|
{{#lookalikes}}
| {{name}} | {{source}} | {{country}} | {{ratio}} | {{size}} | {{status}} |
{{/lookalikes}}

---

## Exclusion audiences

| Name | Source | Retention | Status |
|---|---|---|---|
{{#exclusions}}
| {{name}} | {{source}} | {{retention}} | {{status}} |
{{/exclusions}}

---

## Campaign use matrix

| Campaign type | Include | Exclude |
|---|---|---|
{{#campaign_uses}}
| {{type}} | {{includes}} | {{excludes}} |
{{/campaign_uses}}

---

## Next steps

1. Wait 24 hours for audiences to populate (size estimates are initial).
2. Run `/ppc-manager:meta-creative-brief` to prepare creative for prospecting campaigns.
3. Launch campaigns using the matrix above.
