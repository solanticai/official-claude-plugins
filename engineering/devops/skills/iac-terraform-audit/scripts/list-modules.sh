#!/usr/bin/env bash
# Anthril — IaC Terraform Audit: Module Inventory
# Prints one line per detected module: "<kind>:<dir>"

set -euo pipefail

# Terraform / OpenTofu modules (directory containing at least one .tf file)
find . -maxdepth 8 -type f \( -name "*.tf" -o -name "*.tf.json" \) 2>/dev/null \
  | xargs -I{} dirname "{}" 2>/dev/null \
  | sort -u \
  | grep -vE "^\./\.terraform" \
  | while read -r d; do
    echo "terraform:$d"
  done

# Terragrunt
find . -maxdepth 6 -type f -name "terragrunt.hcl" 2>/dev/null | while read -r f; do
  echo "terragrunt:$(dirname "$f")"
done

# Pulumi
find . -maxdepth 6 -type f -name "Pulumi.yaml" 2>/dev/null | while read -r f; do
  echo "pulumi:$(dirname "$f")"
done

# CDK (flagged but not audited by this skill)
[ -f "cdk.json" ] && echo "cdk:."

exit 0
