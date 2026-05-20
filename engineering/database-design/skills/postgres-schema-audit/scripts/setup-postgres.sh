#!/usr/bin/env bash
# setup-postgres.sh — Interactive wizard to configure a Postgres connection.
#
# Usage:
#   bash setup-postgres.sh                        # fully interactive
#   bash setup-postgres.sh --name prod            # name pre-filled
#   bash setup-postgres.sh --url postgres://...   # parse DATABASE_URL
#   bash setup-postgres.sh --no-test              # skip connection test
#   bash setup-postgres.sh --make-active          # set as active after setup
#
# IMPORTANT — run this script in YOUR OWN TERMINAL, not via Claude. The script
# prompts for a password using silent input. Claude Code's bash tool does not
# forward interactive tty input safely, and credentials should never be typed
# into a chat (they would end up in the conversation transcript).
#
# What it does:
#   1. Collects connection details (host, port, database, user, password, sslmode).
#   2. Tests the connection with SELECT 1 (unless --no-test).
#   3. Writes ~/.config/database-design/connections/<name>.env at mode 0600.
#   4. Optionally sets this profile as the active connection.
#   5. Emits a read-only role SQL snippet the user can apply for safer audits.
#
# Security:
#   - Password is read with `read -s` — never echoed, never in shell history.
#   - Env file is created with umask 077 (owner read/write only, mode 0600).
#   - Connection profiles live in the user's config dir, NOT inside the project.
#     This keeps secrets out of any repo and away from accidental git commits.
#   - The setup wizard does NOT write anywhere inside the project root except
#     an optional project-local pointer file at .database-design/active-connection
#     which contains only the profile NAME (no credentials). That file should
#     be added to .gitignore.

set -euo pipefail

CONN_NAME=""
DATABASE_URL=""
SKIP_TEST="false"
MAKE_ACTIVE="false"
PROJECT_POINTER="false"

while [ $# -gt 0 ]; do
  case "$1" in
    --name)        CONN_NAME="$2"; shift 2 ;;
    --url)         DATABASE_URL="$2"; shift 2 ;;
    --no-test)     SKIP_TEST="true"; shift ;;
    --make-active) MAKE_ACTIVE="true"; shift ;;
    --project-pointer) PROJECT_POINTER="true"; shift ;;
    -h|--help)
      sed -n '2,40p' "$0"; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# ----------------------------------------------------------------------------
# Check prerequisites
# ----------------------------------------------------------------------------
if ! command -v psql >/dev/null 2>&1; then
  echo "ERROR: psql is not installed or not on PATH." >&2
  echo "Install the Postgres client:" >&2
  echo "  macOS:   brew install libpq && brew link --force libpq" >&2
  echo "  Ubuntu:  sudo apt install postgresql-client" >&2
  echo "  Fedora:  sudo dnf install postgresql" >&2
  exit 1
fi

CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
CONN_DIR="$CONFIG_HOME/database-design/connections"
ACTIVE_FILE="$CONFIG_HOME/database-design/active-connection"
mkdir -p "$CONN_DIR"
chmod 700 "$CONFIG_HOME/database-design" 2>/dev/null || true
chmod 700 "$CONN_DIR" 2>/dev/null || true

# ----------------------------------------------------------------------------
# Banner
# ----------------------------------------------------------------------------
cat <<'BANNER'
================================================================
  Postgres Connection Setup — database-design plugin
================================================================
This wizard configures a connection profile for any Postgres 13+
database (Supabase, RDS, Cloud SQL, Neon, Railway, self-hosted,
local). Credentials are stored user-global at mode 0600 and never
leave your machine.

Recommended: create a READ-ONLY role specifically for the audit.
A SQL snippet to create one is printed at the end of this wizard.

BANNER

# ----------------------------------------------------------------------------
# Collect connection name
# ----------------------------------------------------------------------------
if [ -z "$CONN_NAME" ]; then
  read -rp "Connection name (e.g. prod, staging, local) [default: default]: " CONN_NAME
  CONN_NAME="${CONN_NAME:-default}"
fi

# Validate name — alphanumerics, dash, underscore only
if ! echo "$CONN_NAME" | grep -Eq '^[a-zA-Z0-9_-]+$'; then
  echo "ERROR: connection name must match [a-zA-Z0-9_-]+  (got: $CONN_NAME)" >&2
  exit 1
fi

ENV_FILE="$CONN_DIR/${CONN_NAME}.env"

if [ -f "$ENV_FILE" ]; then
  read -rp "Profile '$CONN_NAME' already exists. Overwrite? [y/N]: " OVERWRITE
  case "$OVERWRITE" in
    y|Y|yes|YES) ;;
    *) echo "Aborted."; exit 0 ;;
  esac
fi

# ----------------------------------------------------------------------------
# Collect credentials
# ----------------------------------------------------------------------------
PGHOST=""
PGPORT="5432"
PGDATABASE=""
PGUSER=""
PGPASSWORD=""
PGSSLMODE="require"

if [ -n "$DATABASE_URL" ]; then
  # Parse postgres://user:pass@host:port/db?sslmode=X
  # Strip scheme
  URL_NO_SCHEME="${DATABASE_URL#postgres://}"
  URL_NO_SCHEME="${URL_NO_SCHEME#postgresql://}"

  # Extract query string if present
  if [[ "$URL_NO_SCHEME" == *"?"* ]]; then
    URL_QUERY="${URL_NO_SCHEME#*\?}"
    URL_NO_SCHEME="${URL_NO_SCHEME%%\?*}"
    # Look for sslmode=
    if [[ "$URL_QUERY" == *"sslmode="* ]]; then
      PGSSLMODE=$(echo "$URL_QUERY" | sed -n 's/.*sslmode=\([^&]*\).*/\1/p')
    fi
  fi

  # Split userinfo@hostinfo/database
  USERINFO="${URL_NO_SCHEME%%@*}"
  HOSTPART="${URL_NO_SCHEME#*@}"
  PGDATABASE="${HOSTPART#*/}"
  HOSTINFO="${HOSTPART%%/*}"

  PGUSER="${USERINFO%%:*}"
  if [[ "$USERINFO" == *":"* ]]; then
    PGPASSWORD="${USERINFO#*:}"
    # URL-decode common cases
    PGPASSWORD=$(printf '%b' "${PGPASSWORD//%/\\x}")
  fi

  if [[ "$HOSTINFO" == *":"* ]]; then
    PGHOST="${HOSTINFO%%:*}"
    PGPORT="${HOSTINFO##*:}"
  else
    PGHOST="$HOSTINFO"
  fi

  echo "Parsed DATABASE_URL:"
  echo "  host=$PGHOST port=$PGPORT database=$PGDATABASE user=$PGUSER sslmode=$PGSSLMODE"
  echo "  password: (captured, hidden)"
else
  read -rp "Host (e.g. db.abcxyz.supabase.co or localhost): " PGHOST
  read -rp "Port [default: 5432]: " PORT_IN
  PGPORT="${PORT_IN:-5432}"
  read -rp "Database name: " PGDATABASE
  read -rp "Username: " PGUSER
  # Silent password read — the key security property of this script.
  read -rsp "Password: " PGPASSWORD
  echo ""
  read -rp "SSL mode [disable/allow/prefer/require/verify-ca/verify-full — default: require]: " SSL_IN
  PGSSLMODE="${SSL_IN:-require}"
fi

# Basic validation
if [ -z "$PGHOST" ] || [ -z "$PGDATABASE" ] || [ -z "$PGUSER" ]; then
  echo "ERROR: host, database, and user are required." >&2
  exit 1
fi

# ----------------------------------------------------------------------------
# Test connection
# ----------------------------------------------------------------------------
if [ "$SKIP_TEST" != "true" ]; then
  echo ""
  echo "Testing connection with SELECT 1..."

  # Build a libpq-style connection URI for the test. psql reads it from the
  # environment so the password never appears in ps output.
  export PGPASSWORD PGHOST PGPORT PGDATABASE PGUSER PGSSLMODE

  TEST_OUTPUT=$(psql -v ON_ERROR_STOP=1 -At -c "SELECT 1 AS ok, current_database() AS db, current_user AS usr, version() AS ver" 2>&1 || true)
  TEST_EXIT=$?

  if echo "$TEST_OUTPUT" | grep -q '^1|'; then
    echo "  OK — connected"
    SERVER_INFO=$(echo "$TEST_OUTPUT" | head -n1)
    echo "  $SERVER_INFO"
  else
    echo "  FAILED"
    echo "  psql output:"
    echo "$TEST_OUTPUT" | sed 's/^/    /'
    read -rp "Save this profile anyway? [y/N]: " SAVE_ANYWAY
    case "$SAVE_ANYWAY" in
      y|Y|yes|YES) echo "  Saving despite test failure." ;;
      *) echo "Aborted."; unset PGPASSWORD; exit 1 ;;
    esac
  fi
fi

# ----------------------------------------------------------------------------
# Write env file at mode 0600
# ----------------------------------------------------------------------------
OLD_UMASK=$(umask)
umask 077
cat > "$ENV_FILE" <<EOF
# database-design connection profile: $CONN_NAME
# Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# DO NOT COMMIT THIS FILE. Mode 0600, user-global ($CONFIG_HOME).

PGHOST=$PGHOST
PGPORT=$PGPORT
PGDATABASE=$PGDATABASE
PGUSER=$PGUSER
PGPASSWORD=$PGPASSWORD
PGSSLMODE=$PGSSLMODE

# Optional: override default application_name shown in pg_stat_activity
PGAPPNAME=database-design-audit

# Optional: clamp statement timeout for audit queries (milliseconds).
# 30s is plenty for pg_catalog SELECTs; bump for large tables.
PG_STATEMENT_TIMEOUT_MS=30000
EOF
chmod 0600 "$ENV_FILE"
umask "$OLD_UMASK"

echo ""
echo "Profile written: $ENV_FILE"
echo "Permissions: $(stat -c '%a' "$ENV_FILE" 2>/dev/null || stat -f '%Lp' "$ENV_FILE" 2>/dev/null)"

# Scrub password from this shell
unset PGPASSWORD

# ----------------------------------------------------------------------------
# Set active
# ----------------------------------------------------------------------------
if [ "$MAKE_ACTIVE" = "true" ]; then
  echo "$CONN_NAME" > "$ACTIVE_FILE"
  chmod 0600 "$ACTIVE_FILE"
  echo "Active connection set to: $CONN_NAME"
else
  if [ ! -f "$ACTIVE_FILE" ]; then
    echo "$CONN_NAME" > "$ACTIVE_FILE"
    chmod 0600 "$ACTIVE_FILE"
    echo "No active connection was set before — using '$CONN_NAME' as the default."
  fi
fi

# ----------------------------------------------------------------------------
# Optional project-local pointer
# ----------------------------------------------------------------------------
if [ "$PROJECT_POINTER" = "true" ]; then
  mkdir -p .database-design
  echo "$CONN_NAME" > .database-design/active-connection
  chmod 0600 .database-design/active-connection
  echo "Project-local pointer written: .database-design/active-connection"

  # Nudge user to gitignore it
  if [ -f .gitignore ] && ! grep -q '^\.database-design' .gitignore; then
    echo ""
    echo "NOTE: Add this to your .gitignore:"
    echo "  .database-design/"
  elif [ ! -f .gitignore ]; then
    echo ""
    echo "NOTE: Consider adding .database-design/ to a .gitignore."
  fi
fi

# ----------------------------------------------------------------------------
# Read-only role suggestion
# ----------------------------------------------------------------------------
cat <<'ROLE'

================================================================
  Recommended: create a READ-ONLY role for audits
================================================================
The audit only needs SELECT on pg_catalog, information_schema, and
the target schemas. Running it as a superuser or a role with write
privileges is unnecessary risk. Apply this SQL as a superuser to
create a dedicated read-only role, then re-run setup-postgres.sh
with the new role.

----------------------------------------------------------------
-- Create read-only role for schema audits
----------------------------------------------------------------
-- Replace <password> with a strong password you will store in the
-- connection profile.
CREATE ROLE audit_reader WITH LOGIN PASSWORD '<password>';

-- Catalog access (required — every audit query reads from pg_catalog
-- and information_schema)
GRANT USAGE ON SCHEMA pg_catalog       TO audit_reader;
GRANT USAGE ON SCHEMA information_schema TO audit_reader;

-- Grant USAGE + SELECT on every schema you want audited. Repeat per
-- schema. Replace 'public' with your real schema name.
GRANT USAGE ON SCHEMA public TO audit_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO audit_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO audit_reader;

-- Optional: function signatures (not bodies) are visible via pg_proc
-- without extra grants. If you want the role to be able to EXPLAIN a
-- function, grant EXECUTE on a per-function basis.

-- Verify:
--   psql -U audit_reader -d <db> -c "SELECT count(*) FROM pg_catalog.pg_class"
----------------------------------------------------------------

For Supabase specifically, create the role in the SQL editor and
do NOT grant any role memberships (anon, authenticated, service_role).
The audit does not need RLS bypass.

================================================================
  Setup complete.
================================================================
Next steps:
  1. (Optional) Apply the read-only role SQL above.
  2. Return to Claude Code and run:
       /database-design:postgres-schema-audit
  3. The skill will detect this connection and use it.

ROLE

exit 0
