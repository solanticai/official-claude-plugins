#!/usr/bin/env bash
# Anthril — DevOps Needs Assessment: Stack Detection
# Prints a one-line-per-signal fingerprint of the repo.
# Safe to run in any directory; never mutates.

set -euo pipefail

if [ ! -d "." ]; then
  echo "no-repo"
  exit 0
fi

# Language
LANG_HITS=""
[ -f "package.json" ] && LANG_HITS="${LANG_HITS} javascript/typescript"
[ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ] && LANG_HITS="${LANG_HITS} python"
[ -f "go.mod" ] && LANG_HITS="${LANG_HITS} go"
[ -f "Cargo.toml" ] && LANG_HITS="${LANG_HITS} rust"
[ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ] && LANG_HITS="${LANG_HITS} java/kotlin"
[ -f "Gemfile" ] && LANG_HITS="${LANG_HITS} ruby"
[ -f "composer.json" ] && LANG_HITS="${LANG_HITS} php"
ls *.csproj >/dev/null 2>&1 && LANG_HITS="${LANG_HITS} dotnet"

# Hosting
HOST_HITS=""
[ -f "vercel.json" ] || [ -d ".vercel" ] && HOST_HITS="${HOST_HITS} vercel"
[ -f "netlify.toml" ] && HOST_HITS="${HOST_HITS} netlify"
[ -f "Procfile" ] || [ -f "app.json" ] && HOST_HITS="${HOST_HITS} heroku"
[ -f "fly.toml" ] && HOST_HITS="${HOST_HITS} fly"
[ -f "render.yaml" ] && HOST_HITS="${HOST_HITS} render"
[ -f "amplify.yml" ] && HOST_HITS="${HOST_HITS} amplify"
[ -f "wrangler.toml" ] || [ -f "wrangler.json" ] && HOST_HITS="${HOST_HITS} cloudflare"

# CI/CD
CI_HITS=""
[ -d ".github/workflows" ] && CI_HITS="${CI_HITS} github-actions"
[ -f ".gitlab-ci.yml" ] && CI_HITS="${CI_HITS} gitlab-ci"
[ -f ".circleci/config.yml" ] && CI_HITS="${CI_HITS} circleci"
[ -f "azure-pipelines.yml" ] && CI_HITS="${CI_HITS} azure-pipelines"
[ -f "Jenkinsfile" ] && CI_HITS="${CI_HITS} jenkins"
[ -f "bitbucket-pipelines.yml" ] && CI_HITS="${CI_HITS} bitbucket"

# Containers
CONT_HITS=""
ls Dockerfile* >/dev/null 2>&1 && CONT_HITS="${CONT_HITS} dockerfile"
ls docker-compose*.yml >/dev/null 2>&1 && CONT_HITS="${CONT_HITS} docker-compose"

# IaC
IAC_HITS=""
ls *.tf >/dev/null 2>&1 || find . -maxdepth 3 -name "*.tf" 2>/dev/null | head -1 | grep -q . && IAC_HITS="${IAC_HITS} terraform"
[ -f "terragrunt.hcl" ] && IAC_HITS="${IAC_HITS} terragrunt"
[ -f "Pulumi.yaml" ] && IAC_HITS="${IAC_HITS} pulumi"
[ -f "cdk.json" ] && IAC_HITS="${IAC_HITS} cdk"
find . -maxdepth 3 -name "*.bicep" 2>/dev/null | head -1 | grep -q . && IAC_HITS="${IAC_HITS} bicep"

# Kubernetes
K8S_HITS=""
[ -d "kubernetes" ] || [ -d "k8s" ] || [ -d "manifests" ] && K8S_HITS="${K8S_HITS} manifests"
find . -maxdepth 4 -name "Chart.yaml" 2>/dev/null | head -1 | grep -q . && K8S_HITS="${K8S_HITS} helm"
find . -maxdepth 4 -name "kustomization.yaml" 2>/dev/null | head -1 | grep -q . && K8S_HITS="${K8S_HITS} kustomize"

# Observability
OBS_HITS=""
grep -rqE "pino|winston|bunyan|zap|logrus|zerolog|structlog" --include="*.ts" --include="*.js" --include="*.go" --include="*.py" . 2>/dev/null && OBS_HITS="${OBS_HITS} structured-logging"
grep -rqE "@opentelemetry|opentelemetry-|sentry|datadog" --include="*.ts" --include="*.js" --include="*.go" --include="*.py" . 2>/dev/null && OBS_HITS="${OBS_HITS} tracing"
find . -maxdepth 4 -name "prometheus*.yml" 2>/dev/null | head -1 | grep -q . && OBS_HITS="${OBS_HITS} prometheus"
find . -maxdepth 4 -name "alertmanager*.yml" 2>/dev/null | head -1 | grep -q . && OBS_HITS="${OBS_HITS} alertmanager"

# Runbooks / SRE
SRE_HITS=""
find . -maxdepth 3 -iname "runbook*" 2>/dev/null | head -1 | grep -q . && SRE_HITS="${SRE_HITS} runbooks"
find . -maxdepth 3 -iname "slo*.yaml" 2>/dev/null | head -1 | grep -q . && SRE_HITS="${SRE_HITS} slo-files"
find . -maxdepth 3 -iname "postmortem*" 2>/dev/null | head -1 | grep -q . && SRE_HITS="${SRE_HITS} postmortems"

# Emit
echo "languages:${LANG_HITS:- none}"
echo "hosting:${HOST_HITS:- none}"
echo "ci-cd:${CI_HITS:- none}"
echo "containers:${CONT_HITS:- none}"
echo "iac:${IAC_HITS:- none}"
echo "kubernetes:${K8S_HITS:- none}"
echo "observability:${OBS_HITS:- none}"
echo "sre:${SRE_HITS:- none}"
