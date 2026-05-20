#!/usr/bin/env bash
# Anthril — Observability Audit: Metrics Scanner
# Emits one line per file that emits metrics, plus any Prometheus config.

set -euo pipefail

# Metric emission libraries
grep -rlE "(prom-client|prometheus_client|micrometer|statsd|go-metrics|OpenMetrics|metrics-exporter)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.go" --include="*.py" --include="*.java" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | while read -r f; do
    echo "metric-lib:$f"
  done

# Prometheus configuration and rules
find . -maxdepth 6 -type f \( -name "prometheus*.yml" -o -name "prometheus*.yaml" -o -name "*.rules.yml" -o -name "*.rules.yaml" \) 2>/dev/null | while read -r f; do
  echo "prom-config:$f"
done

# ServiceMonitor / PodMonitor (Prometheus Operator)
grep -rlE "kind:\\s*(ServiceMonitor|PodMonitor|PrometheusRule)" \
  --include="*.yml" --include="*.yaml" \
  --exclude-dir=node_modules --exclude-dir=.git \
  . 2>/dev/null | head -20 | while read -r f; do
    echo "prom-operator-cr:$f"
  done

# Metric emission sites (rough grep for counter/histogram/gauge instantiation)
grep -rnE "(Counter|Histogram|Gauge|Summary)\\s*\\(\\s*['\"][a-z_]+" \
  --include="*.ts" --include="*.js" --include="*.go" --include="*.py" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | head -50 | while read -r line; do
    echo "metric-site:$line"
  done

exit 0
