#!/usr/bin/env bash
# extract-cron.sh — Find all scheduled job definitions in a project.
# Usage: bash scripts/extract-cron.sh <project-root>
# Output: Plain-text listing of cron sources. Always exits 0.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

if command -v rg >/dev/null 2>&1; then
  RG_CMD=(rg --no-heading --line-number --color never
          --glob '!node_modules/**' --glob '!.git/**' --glob '!.next/**'
          --glob '!dist/**' --glob '!build/**' --glob '!.venv/**' --glob '!venv/**')
else
  RG_CMD=(grep -rn --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.next
          --exclude-dir=dist --exclude-dir=build --exclude-dir=.venv --exclude-dir=venv)
fi

run() {
  "${RG_CMD[@]}" "$@" 2>/dev/null || true
}

COUNT=0

emit_section() {
  local label="$1"; shift
  local found
  found=$(run "$@")
  if [ -n "$found" ]; then
    echo "=== $label ==="
    echo "$found"
    COUNT=$((COUNT + $(echo "$found" | grep -c . )))
    echo ""
  fi
}

emit_section "NestJS @Cron decorators" -e '@Cron\s*\('
emit_section "node-cron schedule"      -e 'cron\.schedule\s*\('
emit_section "BullMQ repeat jobs"      -e '\brepeat\s*:\s*\{[^}]*cron'
emit_section "node-schedule"           -e 'schedule\.scheduleJob\s*\('
emit_section "Celery beat (Python)"    -e 'beat_schedule\s*='
emit_section "APScheduler (Python)"    -e 'add_job\s*\(|BackgroundScheduler'
emit_section "Django-Q / django-celery-beat" -e "CrontabSchedule\.objects|Q_CLUSTER"
emit_section "Rails whenever / clockwork" -e "every\s+\d+\.(minute|hour|day)\.do|Clockwork\.every"
emit_section "sidekiq-cron / sidekiq-scheduler" -e "Sidekiq::Cron|sidekiq_scheduler"
emit_section "Laravel schedule"        -e '\$schedule->\w+\('
emit_section "Go robfig/cron"          -e 'cron\.New\(|\.AddFunc\s*\('
emit_section "pg_cron"                 -e 'cron\.schedule\s*\('
emit_section "Supabase schedules"      -e 'supabase\.cron\.schedule'
emit_section "GitHub Actions schedule" -e '^[[:space:]]*-\s*cron\s*:'
emit_section "Vercel Cron (vercel.json)" -e '"crons"\s*:'

echo "=== Summary ==="
echo "  Total scheduled job references: $COUNT"

exit 0
