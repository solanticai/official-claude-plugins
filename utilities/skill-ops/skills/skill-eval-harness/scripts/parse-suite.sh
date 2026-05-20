#!/usr/bin/env bash
# parse-suite.sh — convert evals/suite.yaml to JSON on stdout.
#
# Usage: parse-suite.sh <suite.yaml>
#
# Prefers `yq` if available; otherwise falls back to a minimal awk parser
# that handles the documented suite schema (skill, description, test_cases
# with id/kind/description/user_input/expected_*/judge_criteria/timeout_seconds/tags).
#
# Exit codes:
#   0 — JSON written to stdout
#   1 — file missing or malformed

set -u

SUITE="${1:-}"
if [ -z "$SUITE" ] || [ ! -f "$SUITE" ]; then
  echo "{\"error\":\"suite-missing\",\"path\":\"$SUITE\"}" >&2
  exit 1
fi

if command -v yq >/dev/null 2>&1; then
  yq -o=json '.' "$SUITE"
  exit $?
fi

# Awk fallback — produces a JSON object matching the schema. Lossy on
# string escaping; the harness uses this only for top-level structure
# and re-reads specific fields via Grep when precision matters.
awk '
function esc(s) { gsub(/\\/, "\\\\", s); gsub(/"/, "\\\"", s); gsub(/\t/, "\\t", s); return s }
BEGIN {
  in_cases=0; in_outputs=0; in_criteria=0; in_tags=0;
  printf "{"
}
/^skill:[[:space:]]*/ {
  v=$0; sub(/^skill:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf "\"skill\":\"%s\",", esc(v); next
}
/^description:[[:space:]]*/ {
  v=$0; sub(/^description:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf "\"description\":\"%s\",", esc(v); next
}
/^test_cases:/ { in_cases=1; printf "\"test_cases\":["; first_case=1; next }
in_cases && /^[[:space:]]+-[[:space:]]+id:/ {
  if (!first_case) printf "},"
  first_case=0
  id=$0; sub(/.*id:[[:space:]]*/, "", id); gsub(/[[:space:]]+$/, "", id);
  printf "{\"id\":\"%s\"", esc(id)
  in_outputs=0; in_criteria=0; in_tags=0
  next
}
in_cases && /^[[:space:]]+kind:[[:space:]]*/ {
  v=$0; sub(/.*kind:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf ",\"kind\":\"%s\"", esc(v); next
}
in_cases && /^[[:space:]]+description:[[:space:]]*/ {
  v=$0; sub(/.*description:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf ",\"description\":\"%s\"", esc(v); next
}
in_cases && /^[[:space:]]+user_input:[[:space:]]*/ {
  v=$0; sub(/.*user_input:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  # Strip surrounding quotes if present.
  gsub(/^"|"$/, "", v); gsub(/^'\''|'\''$/, "", v);
  printf ",\"user_input\":\"%s\"", esc(v); next
}
in_cases && /^[[:space:]]+expected_activation:[[:space:]]*/ {
  v=$0; sub(/.*expected_activation:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf ",\"expected_activation\":%s", (v=="true"?"true":"false"); next
}
in_cases && /^[[:space:]]+expected_error:[[:space:]]*/ {
  v=$0; sub(/.*expected_error:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  gsub(/^"|"$/, "", v); gsub(/^'\''|'\''$/, "", v);
  printf ",\"expected_error\":\"%s\"", esc(v); next
}
in_cases && /^[[:space:]]+timeout_seconds:[[:space:]]*/ {
  v=$0; sub(/.*timeout_seconds:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf ",\"timeout_seconds\":%s", v; next
}
in_cases && /^[[:space:]]+expected_outputs:/ {
  if (in_outputs) printf "]"
  if (in_criteria) printf "]"
  if (in_tags) printf "]"
  in_outputs=1; in_criteria=0; in_tags=0
  printf ",\"expected_outputs\":[" ; first_out=1; next
}
in_cases && /^[[:space:]]+judge_criteria:/ {
  if (in_outputs) printf "]"
  if (in_criteria) printf "]"
  if (in_tags) printf "]"
  in_outputs=0; in_criteria=1; in_tags=0
  printf ",\"judge_criteria\":["; first_crit=1; next
}
in_outputs && /^[[:space:]]+-[[:space:]]+kind:/ {
  if (!first_out) printf "},"
  first_out=0
  v=$0; sub(/.*kind:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  printf "{\"kind\":\"%s\"", esc(v); next
}
in_outputs && /^[[:space:]]+(path_glob|text|pattern|value):/ {
  v=$0; sub(/.*(path_glob|text|pattern|value):[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v);
  gsub(/^"|"$/, "", v); gsub(/^'\''|'\''$/, "", v);
  field=$0; sub(/[[:space:]]+/, "", field); sub(/:.*/, "", field); gsub(/^-/, "", field);
  printf ",\"%s\":\"%s\"", field, esc(v); next
}
in_criteria && /^[[:space:]]+-[[:space:]]+/ {
  if (!first_crit) printf ","
  first_crit=0
  v=$0; sub(/^[[:space:]]+-[[:space:]]+/, "", v); gsub(/[[:space:]]+$/, "", v);
  gsub(/^"|"$/, "", v); gsub(/^'\''|'\''$/, "", v);
  printf "\"%s\"", esc(v); next
}
END {
  if (in_outputs) printf "]"
  if (in_criteria) printf "]"
  if (in_cases && !first_case) printf "}"
  if (in_cases) printf "]"
  printf "}\n"
}
' "$SUITE"
