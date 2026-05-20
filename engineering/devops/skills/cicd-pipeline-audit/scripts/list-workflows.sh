#!/usr/bin/env bash
# Anthril — CI/CD Pipeline Audit: Workflow Inventory
# Prints one line per detected CI/CD config: "<platform>:<path>"

set -euo pipefail

# GitHub Actions
if [ -d ".github/workflows" ]; then
  find .github/workflows -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null | while read -r f; do
    echo "github-actions:$f"
  done
fi

# GitLab CI
[ -f ".gitlab-ci.yml" ] && echo "gitlab-ci:.gitlab-ci.yml"
if [ -d ".gitlab" ]; then
  find .gitlab -maxdepth 2 -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null | while read -r f; do
    echo "gitlab-ci:$f"
  done
fi

# CircleCI
[ -f ".circleci/config.yml" ] && echo "circleci:.circleci/config.yml"
[ -f ".circleci/config.yaml" ] && echo "circleci:.circleci/config.yaml"

# Azure Pipelines
[ -f "azure-pipelines.yml" ] && echo "azure-pipelines:azure-pipelines.yml"
[ -f "azure-pipelines.yaml" ] && echo "azure-pipelines:azure-pipelines.yaml"
if [ -d ".azure" ]; then
  find .azure -maxdepth 2 -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null | while read -r f; do
    echo "azure-pipelines:$f"
  done
fi

# Jenkins
[ -f "Jenkinsfile" ] && echo "jenkins:Jenkinsfile"
if [ -d "jenkins" ]; then
  find jenkins -maxdepth 2 -type f -name "Jenkinsfile*" 2>/dev/null | while read -r f; do
    echo "jenkins:$f"
  done
fi

# Bitbucket
[ -f "bitbucket-pipelines.yml" ] && echo "bitbucket:bitbucket-pipelines.yml"
[ -f "bitbucket-pipelines.yaml" ] && echo "bitbucket:bitbucket-pipelines.yaml"

# Drone
[ -f ".drone.yml" ] && echo "drone:.drone.yml"

# Woodpecker
[ -f ".woodpecker.yml" ] && echo "woodpecker:.woodpecker.yml"

exit 0
