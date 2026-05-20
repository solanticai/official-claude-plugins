#!/usr/bin/env bash
# Anthril — Kubernetes Manifest Audit: Inventory
# Prints one line per detected group: "<kind>:<path>"

set -euo pipefail

# Helm charts
find . -maxdepth 6 -type f -name "Chart.yaml" 2>/dev/null | while read -r f; do
  echo "helm-chart:$(dirname "$f")"
done

# Kustomize overlays
find . -maxdepth 6 -type f -name "kustomization.yaml" 2>/dev/null | while read -r f; do
  echo "kustomize:$(dirname "$f")"
done

# Raw manifest directories (contain at least one YAML with `kind:`)
for dir in kubernetes k8s manifests deploy deployments; do
  [ -d "$dir" ] && echo "raw-manifests:$dir"
done

# Look for any top-level YAML file with `kind:` that isn't inside a helm/kustomize dir
find . -maxdepth 4 -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null \
  | grep -vE "node_modules|\.github/|\.gitlab|\.circleci|charts/|kustomiz" \
  | while read -r f; do
    if grep -q "^kind:" "$f" 2>/dev/null; then
      # Only report the directory once
      echo "raw-manifests:$(dirname "$f")"
    fi
  done | sort -u

exit 0
