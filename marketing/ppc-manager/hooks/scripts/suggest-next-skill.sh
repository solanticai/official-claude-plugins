#!/usr/bin/env bash
# ppc-manager Stop hook — suggests a logical next skill based on the most
# recent ppc-manager skill invoked in the current transcript. Non-blocking.

set -e

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

DETECTED=""
# Ordered list — first match wins, so put more specific skills first.
for skill in \
  oauth-setup \
  gtm-setup gtm-datalayer gtm-tags \
  ga4-setup ga4-events \
  google-ads-account-setup google-search-campaign google-pmax-campaign google-ads-copy display-ad-specs \
  meta-pixel-setup meta-capi-setup meta-events-mapping meta-audience-builder meta-creative-brief meta-ads-copy \
  keyword-research campaign-audit utm-builder landing-page-copy youtube-campaign
do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "ppc-manager:$skill"; then
    DETECTED="$skill"
  fi
done

if [ -z "$DETECTED" ]; then
  exit 0
fi

case "$DETECTED" in
  oauth-setup)               NEXT='Now try /ppc-manager:gtm-setup or /ppc-manager:ga4-setup.' ;;
  gtm-setup)                 NEXT='Next up: /ppc-manager:gtm-datalayer to design the dataLayer schema.' ;;
  gtm-datalayer)             NEXT='Next: /ppc-manager:gtm-tags to wire up tracking, or /ppc-manager:ga4-events to align events.' ;;
  gtm-tags)                  NEXT='Consider /ppc-manager:ga4-events or /ppc-manager:meta-pixel-setup next.' ;;
  ga4-setup)                 NEXT='Next: /ppc-manager:ga4-events to define the event taxonomy.' ;;
  ga4-events)                NEXT='Next: /ppc-manager:meta-events-mapping or /ppc-manager:google-ads-account-setup.' ;;
  google-ads-account-setup)  NEXT='Next: /ppc-manager:google-search-campaign or /ppc-manager:google-pmax-campaign.' ;;
  google-search-campaign)    NEXT='Consider /ppc-manager:keyword-research and /ppc-manager:google-ads-copy alongside.' ;;
  google-pmax-campaign)      NEXT='Consider /ppc-manager:display-ad-specs and /ppc-manager:google-ads-copy alongside.' ;;
  google-ads-copy)           NEXT='Pair with /ppc-manager:landing-page-copy for consistent messaging.' ;;
  display-ad-specs)          NEXT='Plug the specs into /ppc-manager:google-pmax-campaign.' ;;
  meta-pixel-setup)          NEXT='Next: /ppc-manager:meta-capi-setup for server-side events.' ;;
  meta-capi-setup)           NEXT='Next: /ppc-manager:meta-events-mapping to unify event taxonomy.' ;;
  meta-events-mapping)       NEXT='Consider /ppc-manager:meta-audience-builder next.' ;;
  meta-audience-builder)     NEXT='Pair with /ppc-manager:meta-creative-brief for new campaigns.' ;;
  meta-creative-brief)       NEXT='Pair with /ppc-manager:meta-ads-copy for finished creative.' ;;
  meta-ads-copy)             NEXT='Pair with /ppc-manager:landing-page-copy for consistent messaging.' ;;
  keyword-research)          NEXT='Feed the output into /ppc-manager:google-search-campaign.' ;;
  campaign-audit)            NEXT='Act on the top fixes, then re-run /ppc-manager:campaign-audit to verify.' ;;
  utm-builder)               NEXT='Use the URLs inside /ppc-manager:google-search-campaign or Meta campaigns.' ;;
  landing-page-copy)         NEXT='Iterate with /ppc-manager:campaign-audit on the live campaign.' ;;
  youtube-campaign)          NEXT='Run /ppc-manager:campaign-audit after first week of spend.' ;;
  *)                         exit 0 ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
