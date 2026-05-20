#!/usr/bin/env bash
# Anthril — DevSecOps Supply Chain: Ecosystem Detection
# Prints one line per detected ecosystem: "<ecosystem>:<manifest_path>"

set -euo pipefail

# npm / pnpm / yarn
if [ -f "package.json" ]; then
  if [ -f "pnpm-lock.yaml" ]; then
    echo "pnpm:package.json"
  elif [ -f "yarn.lock" ]; then
    echo "yarn:package.json"
  else
    echo "npm:package.json"
  fi
fi

# Nested package.json (monorepo)
find . -maxdepth 4 -type f -name "package.json" 2>/dev/null \
  | grep -v "^./package.json$" \
  | grep -v "node_modules" \
  | head -20 \
  | while read -r f; do
    echo "npm:$f"
  done

# Python
[ -f "pyproject.toml" ] && echo "poetry:pyproject.toml"
[ -f "requirements.txt" ] && echo "pip:requirements.txt"
[ -f "Pipfile" ] && echo "pipenv:Pipfile"
[ -f "setup.py" ] && echo "pip:setup.py"

# Go
[ -f "go.mod" ] && echo "go:go.mod"

# Ruby
[ -f "Gemfile" ] && echo "bundler:Gemfile"

# Rust
[ -f "Cargo.toml" ] && echo "cargo:Cargo.toml"

# Java
[ -f "pom.xml" ] && echo "maven:pom.xml"
[ -f "build.gradle" ] && echo "gradle:build.gradle"
[ -f "build.gradle.kts" ] && echo "gradle:build.gradle.kts"

# PHP
[ -f "composer.json" ] && echo "composer:composer.json"

# .NET
ls *.csproj >/dev/null 2>&1 && echo "nuget:*.csproj"

# Docker (for image dependency scanning)
find . -maxdepth 5 -type f -name "Dockerfile*" 2>/dev/null | head -5 | while read -r f; do
  echo "docker:$f"
done

# Terraform
find . -maxdepth 4 -type f -name "*.tf" 2>/dev/null | head -1 | grep -q . && echo "terraform:."

exit 0
