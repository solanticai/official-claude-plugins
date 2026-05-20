#!/usr/bin/env bash
# Anthril — Observability Audit: Tracing Scanner
# Emits one line per file that imports a tracing library, plus any OTel config.

set -euo pipefail

# Tracing libraries
grep -rlE "(@opentelemetry/|opentelemetry-|ddtrace|datadog-|@sentry/|sentry-sdk|jaeger|zipkin|honeycomb)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.go" --include="*.py" --include="*.java" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | while read -r f; do
    echo "trace-lib:$f"
  done

# OTel collector configuration
find . -maxdepth 6 -type f \( -name "otel-collector*.yaml" -o -name "otelcol*.yaml" -o -name "otel*.yaml" -o -name "collector-config*.yaml" \) 2>/dev/null | while read -r f; do
  echo "otel-config:$f"
done

# Tracer instantiation sites
grep -rnE "(trace\\.getTracer|opentelemetry\\.trace|tracer\\.start_span|tracer\\.Start)" \
  --include="*.ts" --include="*.js" --include="*.go" --include="*.py" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | head -50 | while read -r line; do
    echo "tracer-site:$line"
  done

# Sampling configuration hints
grep -rnE "(AlwaysOnSampler|AlwaysOffSampler|TraceIdRatioBasedSampler|ParentBasedSampler|tail_sampling)" \
  --include="*.ts" --include="*.js" --include="*.go" --include="*.py" --include="*.yaml" --include="*.yml" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
  . 2>/dev/null | head -20 | while read -r line; do
    echo "sampling:$line"
  done

exit 0
