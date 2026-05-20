# Tests

Smoke tests for plugin-level scripts shipped in the 2.8.x + 2.9.0 lines.

## Run

```bash
# Pure stdlib unittest (no pytest required)
python tests/scripts/test_smoke.py

# Or via pytest if installed
python -m pytest tests/scripts/test_smoke.py -v
```

## Coverage (18 tests)

### Python scripts (12 tests — always run)

| Script | Test class | Cases |
|---|---|---|
| `lifestyle/health-wellness/scripts/macro-calc.py` | `TestMacroCalc` | maintenance / recomp / aggressive-loss-warn |
| `lifestyle/personal-finance/scripts/retirement-projection.py` | `TestRetirementProjection` | sustained / depleted |
| `lifestyle/personal-finance/scripts/debt-payoff-calc.py` | `TestDebtPayoffCalc` | both / avalanche-only |
| `data-science/experimentation/scripts/power-calc.py` | `TestPowerCalc` | standard A/B / smaller-MDE-bigger-N |
| `economics/business-economics/scripts/cvp-calc.py` | `TestCvpCalc` | basic break-even / negative-margin-errors |
| `utilities/utilities/scripts/link-check.py` | `TestLinkCheck` | offline internal-link detection |

### Bash scripts (6 tests — skipped on Windows without WSL bash)

| Script | Test class | Cases |
|---|---|---|
| `utilities/utilities/skills/audit-resolver/scripts/parse-audit-report.sh` | `TestParseAuditReport` | table-format / bullet-format / empty / missing-file |
| `utilities/utilities/skills/audit-resolver/scripts/verify-stack.sh` | `TestVerifyStack` | marketplace-stack-detect / empty-dir |

The bash-script test classes are decorated with `@unittest.skipUnless(BASH_OK, ...)` and gracefully skip if `bash` isn't directly invocable from the Python subprocess module on this host (e.g. Windows without WSL on PATH). On Linux / macOS / WSL they run.

Pure stdlib only — no third-party dependencies. Tests complete in ~0.7s total.
