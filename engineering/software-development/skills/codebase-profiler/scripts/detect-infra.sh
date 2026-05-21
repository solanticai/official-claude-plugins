#!/usr/bin/env bash
# detect-infra.sh — Detect hosting provider, CI/CD pipelines, and Docker/IaC presence
# Usage: detect-infra.sh <target_dir>
# Output: JSON to stdout

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

# Hosting detection
HOSTING="unknown"
HOSTING_FILE=""

if [[ -f "$TARGET/vercel.json" ]] || [[ -f "$TARGET/.vercelignore" ]]; then
  HOSTING="Vercel"; HOSTING_FILE="vercel.json"
elif [[ -f "$TARGET/fly.toml" ]]; then
  HOSTING="Fly.io"; HOSTING_FILE="fly.toml"
elif [[ -f "$TARGET/wrangler.toml" ]] || [[ -f "$TARGET/wrangler.json" ]]; then
  HOSTING="Cloudflare Workers/Pages"; HOSTING_FILE="wrangler.toml"
elif [[ -f "$TARGET/netlify.toml" ]] || [[ -f "$TARGET/_redirects" ]]; then
  HOSTING="Netlify"; HOSTING_FILE="netlify.toml"
elif [[ -f "$TARGET/railway.json" ]] || [[ -f "$TARGET/railway.toml" ]]; then
  HOSTING="Railway"; HOSTING_FILE="railway.json"
elif [[ -f "$TARGET/render.yaml" ]]; then
  HOSTING="Render"; HOSTING_FILE="render.yaml"
elif [[ -f "$TARGET/app.yaml" ]]; then
  HOSTING="Google App Engine"; HOSTING_FILE="app.yaml"
elif [[ -f "$TARGET/Procfile" ]]; then
  HOSTING="Heroku/Render/Railway"; HOSTING_FILE="Procfile"
elif [[ -f "$TARGET/serverless.yml" ]]; then
  HOSTING="Serverless Framework"; HOSTING_FILE="serverless.yml"
elif [[ -n "$(find "$TARGET" -maxdepth 4 -name "*.yaml" -path "*/k8s/*" 2>/dev/null | head -1)" ]]; then
  HOSTING="Kubernetes"; HOSTING_FILE="k8s/"
fi

# Docker
DOCKER="false"
DOCKER_COMPOSE="false"
[[ -f "$TARGET/Dockerfile" ]] || [[ -n "$(find "$TARGET" -maxdepth 2 -name "Dockerfile*" 2>/dev/null | head -1)" ]] && DOCKER="true"
[[ -f "$TARGET/docker-compose.yml" ]] || [[ -f "$TARGET/docker-compose.yaml" ]] && DOCKER_COMPOSE="true"

# IaC
IAC_TOOLS="[]"
IAC_LIST=""
[[ -f "$TARGET/cdk.json" ]] && IAC_LIST="$IAC_LIST\"AWS CDK\","
[[ -f "$TARGET/sam.yaml" ]] || [[ -f "$TARGET/template.yaml" ]] && IAC_LIST="$IAC_LIST\"AWS SAM\","
[[ -n "$(find "$TARGET" -maxdepth 4 -name "*.tf" 2>/dev/null | head -1)" ]] && IAC_LIST="$IAC_LIST\"Terraform\","
[[ -n "$(find "$TARGET" -maxdepth 3 -name "pulumi.yaml" 2>/dev/null | head -1)" ]] && IAC_LIST="$IAC_LIST\"Pulumi\","
[[ -n "$(find "$TARGET" -maxdepth 3 -name "*.bicep" 2>/dev/null | head -1)" ]] && IAC_LIST="$IAC_LIST\"Bicep\","
[[ -n "$IAC_LIST" ]] && IAC_TOOLS="[${IAC_LIST%,}]"

# CI/CD detection
CI_PROVIDERS="[]"
CI_LIST=""
GHA_WORKFLOWS=0
[[ -d "$TARGET/.github/workflows" ]] && {
  CI_LIST="$CI_LIST\"GitHub Actions\","
  GHA_WORKFLOWS=$(find "$TARGET/.github/workflows" -name "*.yml" -o -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
}
[[ -f "$TARGET/.gitlab-ci.yml" ]] && CI_LIST="$CI_LIST\"GitLab CI\","
[[ -f "$TARGET/Jenkinsfile" ]] && CI_LIST="$CI_LIST\"Jenkins\","
[[ -f "$TARGET/.circleci/config.yml" ]] && CI_LIST="$CI_LIST\"CircleCI\","
[[ -f "$TARGET/bitbucket-pipelines.yml" ]] && CI_LIST="$CI_LIST\"Bitbucket Pipelines\","
[[ -f "$TARGET/.buildkite/pipeline.yml" ]] && CI_LIST="$CI_LIST\"Buildkite\","
[[ -f "$TARGET/azure-pipelines.yml" ]] && CI_LIST="$CI_LIST\"Azure DevOps\","
[[ -n "$CI_LIST" ]] && CI_PROVIDERS="[${CI_LIST%,}]"

# Multi-environment signals
ENV_FILES=$(find "$TARGET" -maxdepth 2 -name ".env*" -not -path "*/.git/*" 2>/dev/null \
  | grep -v "node_modules" | tr '\n' ',' | sed 's/,$//')

# .env.example signal
ENV_EXAMPLE="false"
find "$TARGET" -maxdepth 2 -name ".env.example" -o -name ".env.template" -o -name ".env.sample" 2>/dev/null \
  | grep -q . && ENV_EXAMPLE="true"

# README presence
README="false"
[[ -f "$TARGET/README.md" ]] || [[ -f "$TARGET/README.rst" ]] || [[ -f "$TARGET/README" ]] && README="true"

# CHANGELOG presence
CHANGELOG="false"
[[ -f "$TARGET/CHANGELOG.md" ]] || [[ -f "$TARGET/CHANGELOG" ]] || [[ -f "$TARGET/HISTORY.md" ]] && CHANGELOG="true"

# Pre-commit hooks
PRE_COMMIT="false"
[[ -f "$TARGET/.pre-commit-config.yaml" ]] || [[ -f "$TARGET/.husky/pre-commit" ]] \
  || [[ -f "$TARGET/.git/hooks/pre-commit" ]] && PRE_COMMIT="true"

python3 - <<PYEOF
import json

env_files_raw = "$ENV_FILES"
env_files = [f.strip() for f in env_files_raw.split(",") if f.strip()] if env_files_raw else []

print(json.dumps({
    "hosting": {
        "provider": "$HOSTING",
        "config_file": "$HOSTING_FILE",
        "containerised": $DOCKER == "true" if "$DOCKER" == "true" else False,
        "docker_compose": $DOCKER_COMPOSE == "true" if "$DOCKER_COMPOSE" == "true" else False,
        "iac_tools": $IAC_TOOLS
    },
    "ci_cd": {
        "providers": $CI_PROVIDERS,
        "gha_workflow_count": $GHA_WORKFLOWS
    },
    "env_management": {
        "env_files": env_files,
        "env_example_present": "$ENV_EXAMPLE" == "true"
    },
    "developer_experience": {
        "readme_present": "$README" == "true",
        "changelog_present": "$CHANGELOG" == "true",
        "pre_commit_hooks": "$PRE_COMMIT" == "true"
    }
}, indent=2))
PYEOF
