# YouTube Campaign — {{campaign_name}}

**Goal:** {{goal}}
**Budget:** {{daily_budget}} / day
**Formats:** {{formats}}
**Date:** {{DD_MM_YYYY}}

---

## Campaigns

{{#campaigns}}
### {{name}}

- **Format:** {{format}}
- **Bidding:** {{bidding_strategy}} {{bidding_target}}
- **Audience:** {{audience}}
- **Video asset:** {{video_asset}}
- **Landing page:** {{landing_page}}

{{/campaigns}}

---

## Video asset briefs

{{#assets}}
### {{name}}

- **Duration:** {{duration}}
- **Aspect:** {{aspect}}
- **Dimensions:** {{dimensions}}
- **Hook:** {{hook}}
- **Scene-by-scene:** {{scenes}}
- **CTA:** {{cta}}

{{/assets}}

---

## Companion banner

- **Dimensions:** 300×60 px
- **File:** {{companion_banner_file}}
- **CTA:** {{companion_cta}}

---

## Readiness checklist

- [{{check_channel}}] YouTube channel linked to Google Ads
- [{{check_videos}}] Videos uploaded (public or unlisted)
- [{{check_duration}}] Videos meet format minimums
- [{{check_lp}}] Landing page works
- [{{check_banner}}] Companion banner uploaded
- [{{check_conv}}] Conversion tracking imported
- [{{check_audience}}] Audience defined
- [{{check_budget}}] Budget approved

---

## Next steps

1. Upload videos to YouTube (unlisted).
2. Create campaigns in Google Ads UI (v1.0 MCP doesn't yet support Video campaign creation).
3. Run `/ppc-manager:campaign-audit --scope youtube` after 14 days.
