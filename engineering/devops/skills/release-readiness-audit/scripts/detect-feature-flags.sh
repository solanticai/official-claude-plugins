#!/usr/bin/env bash
# Anthril — Release Readiness: Feature-Flag Detector
# Finds feature-flag library usage and flag references in the current repo.

set -euo pipefail

echo "=== FEATURE-FLAG LIBRARIES ==="
grep -rlE "(@unleash/|unleash-client|launchdarkly|flagsmith|posthog|configcat|split\\.io|growthbook|optimizely)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.go" --include="*.py" --include="*.java" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | head -30

echo ""
echo "=== FLAG-CHECK CALL SITES ==="
grep -rnE "(isFlagEnabled|isEnabled\\(|variation\\(|getFlag\\(|feature_enabled|featureFlag|useFeatureFlag)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.go" --include="*.py" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | head -40

echo ""
echo "=== ENV-VAR FLAG PATTERNS ==="
grep -rnE "process\\.env\\.(FEATURE|FLAG|ENABLE)_[A-Z_]+|os\\.environ\\[['\"](FEATURE|FLAG|ENABLE)_" \
  --include="*.ts" --include="*.js" --include="*.py" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | head -30

echo ""
echo "=== FLAG CONFIG FILES ==="
find . -maxdepth 5 -type f \( -name "flags.yaml" -o -name "flags.json" -o -name "feature-flags.yaml" -o -name "*.flags.yml" -o -name "flagsmith*.json" \) 2>/dev/null | head -10

exit 0
