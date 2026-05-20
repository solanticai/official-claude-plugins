#!/usr/bin/env bash
# Anthril — DevSecOps Supply Chain: Lockfile Scanner
# Emits one line per detected lockfile with a coarse pin-style summary.

set -euo pipefail

# npm / pnpm / yarn
if [ -f "package-lock.json" ]; then
  deps=$(grep -cE "\"resolved\":" package-lock.json 2>/dev/null || echo 0)
  echo "npm-lock:package-lock.json:deps=$deps"
fi
if [ -f "pnpm-lock.yaml" ]; then
  deps=$(grep -cE "^  [a-z@/]" pnpm-lock.yaml 2>/dev/null || echo 0)
  echo "pnpm-lock:pnpm-lock.yaml:deps=$deps"
fi
if [ -f "yarn.lock" ]; then
  deps=$(grep -cE "^[a-z@].+:$" yarn.lock 2>/dev/null || echo 0)
  echo "yarn-lock:yarn.lock:deps=$deps"
fi

# Python
if [ -f "poetry.lock" ]; then
  deps=$(grep -cE "^name = " poetry.lock 2>/dev/null || echo 0)
  echo "poetry-lock:poetry.lock:deps=$deps"
fi
if [ -f "requirements.txt" ]; then
  total=$(grep -cvE "^\\s*#|^\\s*$" requirements.txt 2>/dev/null || echo 0)
  pinned=$(grep -cE "^[a-zA-Z0-9_.-]+==[0-9]" requirements.txt 2>/dev/null || echo 0)
  echo "pip-reqs:requirements.txt:total=$total:pinned=$pinned"
fi
if [ -f "Pipfile.lock" ]; then
  echo "pipenv-lock:Pipfile.lock"
fi

# Go
if [ -f "go.sum" ]; then
  deps=$(wc -l < go.sum 2>/dev/null || echo 0)
  echo "go-sum:go.sum:deps=$deps"
fi

# Ruby
if [ -f "Gemfile.lock" ]; then
  deps=$(grep -cE "^    [a-z]" Gemfile.lock 2>/dev/null || echo 0)
  echo "bundler-lock:Gemfile.lock:deps=$deps"
fi

# Rust
if [ -f "Cargo.lock" ]; then
  deps=$(grep -cE "^name = " Cargo.lock 2>/dev/null || echo 0)
  echo "cargo-lock:Cargo.lock:deps=$deps"
fi

# PHP
if [ -f "composer.lock" ]; then
  deps=$(grep -cE "\"name\":" composer.lock 2>/dev/null || echo 0)
  echo "composer-lock:composer.lock:deps=$deps"
fi

# Terraform
if [ -f ".terraform.lock.hcl" ]; then
  echo "terraform-lock:.terraform.lock.hcl"
fi

# Missing lockfiles when a manifest exists — flag these
[ -f "package.json" ] && ! ls package-lock.json pnpm-lock.yaml yarn.lock >/dev/null 2>&1 \
  && echo "MISSING: package.json has no lockfile"
[ -f "requirements.txt" ] && ! grep -qE "==" requirements.txt 2>/dev/null \
  && echo "WARNING: requirements.txt has no == pins"
[ -f "go.mod" ] && [ ! -f "go.sum" ] \
  && echo "MISSING: go.mod has no go.sum"
[ -f "Gemfile" ] && [ ! -f "Gemfile.lock" ] \
  && echo "MISSING: Gemfile has no Gemfile.lock"
[ -f "Cargo.toml" ] && [ ! -f "Cargo.lock" ] && ! grep -q "^\\[\\[bin\\]\\]" Cargo.toml 2>/dev/null \
  && echo "INFO: Cargo.toml (library?) has no Cargo.lock"

exit 0
