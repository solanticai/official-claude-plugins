# Example: Creating a "Customer Churn Predictor" Skill

## Skill Requirements

| Field | Value |
|-------|-------|
| Name | `customer-churn-predictor` |
| Category | Data Analysis & Intelligence |
| Description | Predict customer churn risk using behavioural signals, usage patterns, and engagement metrics with actionable retention recommendations |
| Complexity | Medium (300 lines) |
| Argument Hint | `[customer-data-description]` |
| Tools | Read Grep Glob Write Edit Bash Agent |
| Subagent | No (interactive analysis) |
| Ultrathink | Yes (complex pattern analysis) |
| Dynamic Context | No |
| Visual Outputs | Mermaid diagram for churn funnel |

## Generated Directory

```
skills/customer-churn-predictor/
├── skill.md              (285 lines)
├── LICENSE.txt
├── templates/
│   └── output-template.md
├── examples/
│   └── example-output.md
└── scripts/
    └── churn-signals.py
```

## Generated SKILL.md (excerpt)

```yaml
---
name: customer-churn-predictor
description: Predict customer churn risk using behavioural signals, usage patterns, and engagement metrics with actionable retention recommendations
argument-hint: [customer-data-description]
allowed-tools: Read Grep Glob Write Edit Bash Agent
---

# Customer Churn Predictor

ultrathink

## User Context

The user has provided the following customer data context:

$ARGUMENTS

If no arguments were provided, begin Phase 1 by asking about the customer data available and business model.

---

## System Prompt

You are a customer analytics specialist who identifies churn risk patterns...
```

## Validation Results

| Check | Status |
|-------|--------|
| SKILL.md under 500 lines | PASS (285 lines) |
| Valid YAML frontmatter | PASS |
| Description under 250 chars | PASS (143 chars) |
| $ARGUMENTS used | PASS |
| ultrathink included | PASS |
| templates/ populated | PASS |
| examples/ populated | PASS |
| reference.md needed | NO (under 400 lines) |
