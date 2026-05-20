# ppc-manager Stop hook — PowerShell sibling of suggest-next-skill.sh.

$ErrorActionPreference = 'SilentlyContinue'

$transcript = $env:CLAUDE_TRANSCRIPT
if (-not $transcript -or -not (Test-Path $transcript)) { exit 0 }

$skills = @(
  'oauth-setup',
  'gtm-setup','gtm-datalayer','gtm-tags',
  'ga4-setup','ga4-events',
  'google-ads-account-setup','google-search-campaign','google-pmax-campaign','google-ads-copy','display-ad-specs',
  'meta-pixel-setup','meta-capi-setup','meta-events-mapping','meta-audience-builder','meta-creative-brief','meta-ads-copy',
  'keyword-research','campaign-audit','utm-builder','landing-page-copy','youtube-campaign'
)

$tail = Get-Content $transcript -Tail 200 -ErrorAction SilentlyContinue
if (-not $tail) { exit 0 }
$joined = $tail -join "`n"
$detected = $null
foreach ($s in $skills) { if ($joined -match "ppc-manager:$s") { $detected = $s } }
if (-not $detected) { exit 0 }

$suggest = switch ($detected) {
  'oauth-setup'              { 'Now try /ppc-manager:gtm-setup or /ppc-manager:ga4-setup.' }
  'gtm-setup'                { 'Next up: /ppc-manager:gtm-datalayer to design the dataLayer schema.' }
  'gtm-datalayer'            { 'Next: /ppc-manager:gtm-tags to wire up tracking.' }
  'gtm-tags'                 { 'Consider /ppc-manager:ga4-events or /ppc-manager:meta-pixel-setup.' }
  'ga4-setup'                { 'Next: /ppc-manager:ga4-events to define the event taxonomy.' }
  'ga4-events'               { 'Next: /ppc-manager:meta-events-mapping or /ppc-manager:google-ads-account-setup.' }
  'google-ads-account-setup' { 'Next: /ppc-manager:google-search-campaign or /ppc-manager:google-pmax-campaign.' }
  'google-search-campaign'   { 'Consider /ppc-manager:keyword-research and /ppc-manager:google-ads-copy.' }
  'google-pmax-campaign'     { 'Consider /ppc-manager:display-ad-specs and /ppc-manager:google-ads-copy.' }
  'google-ads-copy'          { 'Pair with /ppc-manager:landing-page-copy for consistent messaging.' }
  'display-ad-specs'         { 'Plug the specs into /ppc-manager:google-pmax-campaign.' }
  'meta-pixel-setup'         { 'Next: /ppc-manager:meta-capi-setup for server-side events.' }
  'meta-capi-setup'          { 'Next: /ppc-manager:meta-events-mapping to unify event taxonomy.' }
  'meta-events-mapping'      { 'Consider /ppc-manager:meta-audience-builder next.' }
  'meta-audience-builder'    { 'Pair with /ppc-manager:meta-creative-brief for new campaigns.' }
  'meta-creative-brief'      { 'Pair with /ppc-manager:meta-ads-copy for finished creative.' }
  'meta-ads-copy'            { 'Pair with /ppc-manager:landing-page-copy for consistent messaging.' }
  'keyword-research'         { 'Feed the output into /ppc-manager:google-search-campaign.' }
  'campaign-audit'           { 'Act on the top fixes, then re-run /ppc-manager:campaign-audit to verify.' }
  'utm-builder'              { 'Use the URLs inside /ppc-manager:google-search-campaign or Meta campaigns.' }
  'landing-page-copy'        { 'Iterate with /ppc-manager:campaign-audit on the live campaign.' }
  'youtube-campaign'         { 'Run /ppc-manager:campaign-audit after first week of spend.' }
  default                    { $null }
}

if ($suggest) { Write-Output "{`"systemMessage`":`"$suggest`"}" }
exit 0
