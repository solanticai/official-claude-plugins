#!/usr/bin/env bash
# Anthril — DevSecOps Supply Chain: Secret Pattern Scanner
# Scans the current checkout for common secret-shaped strings.
# Reports file:line hits — NEVER prints the secret itself.
# History scanning is out of scope; use gitleaks / trufflehog for that.

set -euo pipefail

# AWS access keys
echo "=== AWS ACCESS KEYS (AKIA...) ==="
grep -rnE "AKIA[0-9A-Z]{16}" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | sed -E 's/(AKIA[0-9A-Z]{4})[0-9A-Z]+/\1[REDACTED]/g' | head -20

echo ""
echo "=== GITHUB TOKENS (ghp_, gho_, ghu_, ghs_) ==="
grep -rnE "gh[pousr]_[A-Za-z0-9]{20,}" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | sed -E 's/(gh[pousr]_[A-Za-z0-9]{4})[A-Za-z0-9]+/\1[REDACTED]/g' | head -20

echo ""
echo "=== SLACK TOKENS (xoxb-, xoxp-, xoxa-) ==="
grep -rnE "xox[bpa]-[0-9]{10,}-[0-9]{10,}" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | sed -E 's/(xox[bpa]-[0-9]{4})[0-9A-Za-z-]+/\1[REDACTED]/g' | head -20

echo ""
echo "=== STRIPE KEYS (sk_live_, pk_live_) ==="
grep -rnE "(sk|pk)_live_[A-Za-z0-9]{20,}" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | sed -E 's/((sk|pk)_live_[A-Za-z0-9]{4})[A-Za-z0-9]+/\1[REDACTED]/g' | head -20

echo ""
echo "=== PRIVATE KEYS ==="
grep -rnE "-----BEGIN (RSA |EC |OPENSSH |DSA |PGP |)PRIVATE KEY-----" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | head -20

echo ""
echo "=== SENDGRID / TWILIO / DATADOG / NEW RELIC ==="
grep -rnE "(SG\\.[A-Za-z0-9_-]{22,}|AC[a-z0-9]{32}|dd_api_key|NRAK-)" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | sed -E 's/(SG\.[A-Za-z0-9_-]{4})[A-Za-z0-9_-]+/\1[REDACTED]/g' | head -20

echo ""
echo "=== TRACKED .env / CREDENTIAL FILES ==="
git ls-files 2>/dev/null | grep -E "(^|/)(\\.env(\\..+)?|credentials\\.json|service-account.*\\.json|\\.npmrc|\\.pypirc|\\.dockercfg|config\\.yaml)$" | head -30

echo ""
echo "=== HIGH-ENTROPY CANDIDATE STRINGS ==="
# Rough entropy heuristic: 32+ char alphanumeric+=/ strings in non-binary files
grep -rnE "['\"][A-Za-z0-9+/=]{32,}['\"]" \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.yaml" --include="*.yml" --include="*.json" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | head -10 | sed -E 's/(['"])[A-Za-z0-9+/=]{4}[A-Za-z0-9+/=]+(['"])/\1[REDACTED]\2/g'

exit 0
