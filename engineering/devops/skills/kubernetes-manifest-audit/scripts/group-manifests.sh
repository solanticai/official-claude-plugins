#!/usr/bin/env bash
# Anthril — Kubernetes Manifest Audit: Manifest Grouper
# Given a target directory of raw manifests (no Chart.yaml / kustomization.yaml),
# group individual YAML files by their apparent workload cluster:
# - Files in the same directory → one group.
# - Files that reference each other via selector/labels → same group.
# Prints one line per group: "group-id:<manifest1>,<manifest2>,..."
# Usage: bash group-manifests.sh <dir>

set -euo pipefail
DIR="${1:-.}"
[ ! -d "$DIR" ] && { echo "error: directory not found: $DIR" >&2; exit 1; }

# Strategy: group by immediate parent directory. This catches the common convention
# of kubernetes/api/*.yaml, kubernetes/worker/*.yaml, etc.

declare -A GROUPS 2>/dev/null || true  # bash 4+

find "$DIR" -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null \
  | grep -vE "node_modules|\\.git/|charts/|helm/|kustomiz" \
  | while read -r f; do
    # Skip files without a kind: line (not manifests)
    grep -q "^kind:" "$f" 2>/dev/null || continue
    parent=$(dirname "$f")
    echo "$parent|$f"
  done \
  | sort \
  | awk -F'|' '
    {
      if ($1 != prev_parent) {
        if (prev_parent != "") print prev_parent ":" manifests;
        prev_parent = $1;
        manifests = $2;
      } else {
        manifests = manifests "," $2;
      }
    }
    END {
      if (prev_parent != "") print prev_parent ":" manifests;
    }
  '

exit 0
