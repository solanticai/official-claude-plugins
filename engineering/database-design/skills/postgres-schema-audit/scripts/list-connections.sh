#!/usr/bin/env bash
# list-connections.sh — Print configured Postgres connection profiles.
# Usage:
#   bash list-connections.sh [--format text|json]
#
# Output: Profile names (with the active one marked). Never prints passwords
# or any credential material — only the profile name, host, port, database,
# user, and sslmode. Safe to share.
#
# Exit 0 always; empty list is not an error.

set -euo pipefail

FORMAT="text"
if [ "${1:-}" = "--format" ] && [ -n "${2:-}" ]; then
  FORMAT="$2"
fi

CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
CONN_DIR="$CONFIG_HOME/database-design/connections"
ACTIVE_FILE="$CONFIG_HOME/database-design/active-connection"

# Resolve active connection (project-local pointer wins)
ACTIVE_CONN=""
if [ -f ".database-design/active-connection" ]; then
  ACTIVE_CONN=$(head -n1 ".database-design/active-connection" | tr -d '[:space:]')
elif [ -f "$ACTIVE_FILE" ]; then
  ACTIVE_CONN=$(head -n1 "$ACTIVE_FILE" | tr -d '[:space:]')
fi

if [ ! -d "$CONN_DIR" ]; then
  case "$FORMAT" in
    json) echo "[]" ;;
    *)    echo "No connections configured. Run: bash setup-postgres.sh" ;;
  esac
  exit 0
fi

# Collect profile metadata (NO credentials)
declare -a NAMES HOSTS PORTS DBS USERS SSLMODES
while IFS= read -r f; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .env)
  # Source in a subshell so the caller's env isn't polluted
  # shellcheck disable=SC1090
  eval "$(
    (
      set -a
      . "$f"
      set +a
      printf 'H=%q\nP=%q\nD=%q\nU=%q\nS=%q\n' \
        "${PGHOST:-}" "${PGPORT:-}" "${PGDATABASE:-}" "${PGUSER:-}" "${PGSSLMODE:-}"
    )
  )"
  NAMES+=("$name")
  HOSTS+=("$H")
  PORTS+=("$P")
  DBS+=("$D")
  USERS+=("$U")
  SSLMODES+=("$S")
done < <(ls -1 "$CONN_DIR"/*.env 2>/dev/null || true)

COUNT=${#NAMES[@]}

case "$FORMAT" in
  json)
    printf '['
    for i in "${!NAMES[@]}"; do
      [ "$i" -gt 0 ] && printf ','
      printf '{"name":"%s","host":"%s","port":"%s","database":"%s","user":"%s","sslmode":"%s","active":%s}' \
        "${NAMES[$i]}" "${HOSTS[$i]}" "${PORTS[$i]}" "${DBS[$i]}" "${USERS[$i]}" "${SSLMODES[$i]}" \
        "$([ "${NAMES[$i]}" = "$ACTIVE_CONN" ] && echo true || echo false)"
    done
    printf ']\n'
    ;;
  text|*)
    if [ "$COUNT" -eq 0 ]; then
      echo "No connections configured. Run: bash setup-postgres.sh"
      exit 0
    fi
    echo "Configured connections ($COUNT):"
    for i in "${!NAMES[@]}"; do
      MARKER="  "
      [ "${NAMES[$i]}" = "$ACTIVE_CONN" ] && MARKER="* "
      printf '%s%-15s  host=%s  port=%s  db=%s  user=%s  sslmode=%s\n' \
        "$MARKER" \
        "${NAMES[$i]}" \
        "${HOSTS[$i]}" \
        "${PORTS[$i]}" \
        "${DBS[$i]}" \
        "${USERS[$i]}" \
        "${SSLMODES[$i]}"
    done
    echo ""
    if [ -n "$ACTIVE_CONN" ]; then
      echo "Active: $ACTIVE_CONN  (* marked above)"
    else
      echo "Active: (none)"
    fi
    ;;
esac

exit 0
