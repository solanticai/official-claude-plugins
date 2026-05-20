#!/usr/bin/env bash
# Anthril — Container Audit: File Inventory
# Prints one line per detected file: "<kind>:<path>"

set -euo pipefail

find . -maxdepth 5 -type f -name "Dockerfile*" 2>/dev/null | while read -r f; do
  echo "dockerfile:$f"
done

find . -maxdepth 5 -type f \( -name "docker-compose*.yml" -o -name "docker-compose*.yaml" -o -name "compose*.yml" -o -name "compose*.yaml" \) 2>/dev/null | while read -r f; do
  echo "compose:$f"
done

find . -maxdepth 5 -type f -name ".dockerignore" 2>/dev/null | while read -r f; do
  echo "dockerignore:$f"
done

if [ -d ".devcontainer" ]; then
  find .devcontainer -maxdepth 2 -type f -name "*.json" 2>/dev/null | while read -r f; do
    echo "devcontainer:$f"
  done
fi

exit 0
