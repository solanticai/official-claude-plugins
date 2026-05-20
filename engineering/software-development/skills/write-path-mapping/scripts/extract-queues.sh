#!/usr/bin/env bash
# extract-queues.sh — Find queue producers and consumers.
# Usage: bash scripts/extract-queues.sh <project-root>
# Output: Plain-text listing of queue-related references. Always exits 0.

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

emit_section() {
  local label="$1"; shift
  local found
  found=$(run "$@")
  if [ -n "$found" ]; then
    echo "=== $label ==="
    echo "$found"
    echo ""
  fi
}

# --- BullMQ / Bull --------------------------------------------------------------------
emit_section "BullMQ producers (Queue.add)"        -e '\bnew\s+Queue\s*\(|\.add\s*\(\s*["'"'"'][^"'"'"']+["'"'"']'
emit_section "BullMQ consumers (Worker)"           -e '\bnew\s+Worker\s*\('
emit_section "Bull producers/consumers"            -e "from\s+['\"]bull['\"]"

# --- AWS SQS --------------------------------------------------------------------------
emit_section "SQS send"                            -e 'SendMessageCommand|sqs\.sendMessage\s*\('
emit_section "SQS receive"                         -e 'ReceiveMessageCommand|sqs\.receiveMessage\s*\('

# --- Kafka ----------------------------------------------------------------------------
emit_section "Kafka producers"                     -e '\.produce\s*\(|producer\.send\s*\('
emit_section "Kafka consumers"                     -e '\.consumer\s*\(|kafka.*\.run\s*\('

# --- RabbitMQ / AMQP ------------------------------------------------------------------
emit_section "AMQP publish"                        -e '\.publish\s*\(|\.sendToQueue\s*\('
emit_section "AMQP consume"                        -e '\.consume\s*\(\s*["'"'"']'

# --- NATS -----------------------------------------------------------------------------
emit_section "NATS publish"                        -e 'nats.*\.publish\s*\(|jetstream.*\.publish\s*\('
emit_section "NATS subscribe"                      -e 'nats.*\.subscribe\s*\('

# --- Postgres PGMQ / pg-boss ----------------------------------------------------------
emit_section "pg-boss / PGMQ"                      -e 'pgmq\.send|pg_boss|\.send\s*\(\s*["'"'"'][a-z_]+["'"'"'].*,'

# --- Redis pubsub / streams -----------------------------------------------------------
emit_section "Redis pubsub publish"                -e '\.publish\s*\(\s*["'"'"'][^"'"'"']+["'"'"']'
emit_section "Redis streams XADD"                  -e '\bXADD\b|\.xadd\s*\('

# --- Supabase queues / realtime -------------------------------------------------------
emit_section "Supabase queue"                      -e 'supabase\.queue|pgmq\.'
emit_section "Supabase realtime broadcast"         -e '\.send\s*\(\s*\{\s*type\s*:\s*["'"'"']broadcast'

# --- Celery ---------------------------------------------------------------------------
emit_section "Celery task definitions"             -e '@(shared_task|app\.task|celery\.task)'
emit_section "Celery invocations"                  -e '\.delay\s*\(|\.apply_async\s*\('

# --- Sidekiq / ActiveJob --------------------------------------------------------------
emit_section "Sidekiq worker / ActiveJob perform"  -e 'include\s+Sidekiq::Worker|<\s*ApplicationJob|\.perform_(async|later)'

# --- Cloudflare Queues ----------------------------------------------------------------
emit_section "Cloudflare Queues"                   -e '\.send\s*\(\s*\{\s*body' -e 'env\.[A-Z_]+_QUEUE\.send'

exit 0
