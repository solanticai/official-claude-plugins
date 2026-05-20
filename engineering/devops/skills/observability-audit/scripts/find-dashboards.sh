#!/usr/bin/env bash
# Anthril — Observability Audit: Dashboard & Alert Finder

set -euo pipefail

echo "=== GRAFANA DASHBOARD DIRS ==="
find . -maxdepth 5 -type d -name "grafana" 2>/dev/null | head -5
find . -maxdepth 5 -type d -name "dashboards" 2>/dev/null | head -5

echo ""
echo "=== GRAFANA DASHBOARD JSON ==="
# Grafana dashboard JSON files usually have "panels" and "dashboard" or "schemaVersion" keys
grep -rlE "\"schemaVersion\"|\"panels\"" \
  --include="*.json" \
  --exclude-dir=node_modules --exclude-dir=.git \
  . 2>/dev/null | head -30

echo ""
echo "=== ALERTMANAGER CONFIG ==="
find . -maxdepth 5 -type f \( -name "alertmanager*.yml" -o -name "alertmanager*.yaml" \) 2>/dev/null | head -10

echo ""
echo "=== PROMETHEUS RULE FILES ==="
find . -maxdepth 6 -type f \( -name "*.rules.yml" -o -name "*.rules.yaml" -o -name "alerting*.yml" \) 2>/dev/null | head -20

echo ""
echo "=== DATADOG DASHBOARDS / MONITORS ==="
grep -rlE "\"type\":\\s*\"monitor\"|\"type\":\\s*\"timeseries\"" \
  --include="*.json" \
  --exclude-dir=node_modules --exclude-dir=.git \
  . 2>/dev/null | head -20

echo ""
echo "=== NEW RELIC / HONEYCOMB / LIGHTSTEP ==="
find . -maxdepth 5 -type f \( -name "newrelic*.yml" -o -name "honeycomb*.yml" -o -name "lightstep*.yml" \) 2>/dev/null | head -10

echo ""
echo "=== PAGERDUTY / OPSGENIE CONFIG ==="
find . -maxdepth 5 -type f \( -name "pagerduty*.yml" -o -name "pagerduty*.yaml" -o -name "opsgenie*.yml" -o -name "opsgenie*.yaml" \) 2>/dev/null | head -10

exit 0
