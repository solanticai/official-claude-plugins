#!/usr/bin/env bash
# Anthril — Observability Audit: Logging Scanner
# Emits one line per file that imports a structured-logging library.

set -euo pipefail

grep -rlE "(^|[^a-zA-Z])(pino|winston|bunyan|zap|logrus|zerolog|structlog|slog)(\\b|\\.|\\[)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.go" --include="*.py" --include="*.java" --include="*.kt" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  . 2>/dev/null | while read -r f; do
    echo "logger:$f"
  done

# Flag bare console.log / print / println calls in service code (rough heuristic)
grep -rlE "console\\.log|^\\s*print\\(|println\\(" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" --include="*.go" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=.next \
  --exclude-dir=tests --exclude-dir=test --exclude-dir=__tests__ \
  . 2>/dev/null | head -30 | while read -r f; do
    echo "bare-console:$f"
  done

# Log shipper configs
find . -maxdepth 6 -type f \( -name "filebeat.yml" -o -name "vector.toml" -o -name "fluent-bit.conf" -o -name "fluentd.conf" -o -name "promtail*.yml" \) 2>/dev/null \
  | while read -r f; do
    echo "shipper:$f"
  done

exit 0
