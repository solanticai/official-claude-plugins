# =============================================================================
# IaC Terraform Audit — Suggested Changes
# Audit ID: {{audit_id}}
# Generated: {{DD/MM/YYYY HH:mm}}
# Mode: {{mode}}
# MANUAL REVIEW REQUIRED — every block may affect real infrastructure.
# DO NOT `terraform apply` blocks without reviewing and planning first.
# =============================================================================

# -----------------------------------------------------------------------------
# IAC-001 — CRITICAL — C.1 (SG port 22 open to world)
# Target: modules/vpc/main.tf:42
# Module: modules/vpc
# Evidence: `cidr_blocks = ["0.0.0.0/0"]` on port 22 ingress rule `ssh-open`.
# -----------------------------------------------------------------------------
# Suggested change:
resource "aws_security_group_rule" "ssh_open" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  # OLD:
  # cidr_blocks       = ["0.0.0.0/0"]
  # NEW:
  cidr_blocks       = [var.bastion_cidr]  # pass from root module
  security_group_id = aws_security_group.web.id
}

# -----------------------------------------------------------------------------
# IAC-002 — HIGH — A.1 (local state backend on production module)
# Target: environments/prod/backend.tf:1
# Module: environments/prod
# -----------------------------------------------------------------------------
# Suggested change: migrate to S3 with DynamoDB locking.
# STATE MIGRATION — requires manual `terraform init -migrate-state`.
terraform {
  backend "s3" {
    bucket         = "acme-tfstate-prod"
    key            = "environments/prod/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "acme-tfstate-locks"
    encrypt        = true
    kms_key_id     = "alias/tfstate"
  }
}

# -----------------------------------------------------------------------------
# IAC-003 — MEDIUM — B.2 (AWS provider unpinned)
# Target: modules/rds/versions.tf:3
# -----------------------------------------------------------------------------
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"  # was: unpinned
    }
  }
}
