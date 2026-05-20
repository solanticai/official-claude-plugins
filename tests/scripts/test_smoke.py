"""Smoke tests for plugin-level scripts shipped in v2.8.x + v2.9.0.

Covers:
- 6 Python scripts (macro-calc, retirement-projection, debt-payoff-calc, power-calc, cvp-calc, link-check)
- 2 Bash scripts (audit-resolver/parse-audit-report.sh, audit-resolver/verify-stack.sh)

Each test invokes the script with a small valid input and asserts:
- Exit code 0 (or expected non-zero for error cases)
- Some expected substring in stdout / stderr

Run from the repo root:

    python -m pytest tests/scripts/test_smoke.py -v

Or without pytest:

    python tests/scripts/test_smoke.py

Pure stdlib — no third-party deps.
"""
from __future__ import annotations

import csv
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run(script: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    """Invoke a plugin script and return the completed-process result."""
    cmd = [sys.executable, str(REPO_ROOT / script), *args]
    return subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


class TestMacroCalc(unittest.TestCase):
    """lifestyle/health-wellness/scripts/macro-calc.py"""

    SCRIPT = "lifestyle/health-wellness/scripts/macro-calc.py"

    def test_maintenance_male(self):
        r = run(self.SCRIPT, "--sex", "M", "--age", "34", "--kg", "80",
                "--cm", "180", "--activity", "1.55", "--goal", "maintenance")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("TDEE", r.stdout)
        self.assertIn("Protein", r.stdout)
        self.assertIn("Carbs", r.stdout)

    def test_recomp_female(self):
        r = run(self.SCRIPT, "--sex", "F", "--age", "30", "--kg", "65",
                "--cm", "168", "--activity", "1.55", "--goal", "recomp")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Target", r.stdout)

    def test_aggressive_loss_warns(self):
        r = run(self.SCRIPT, "--sex", "M", "--age", "40", "--kg", "100",
                "--cm", "175", "--activity", "1.2", "--goal", "agg_loss")
        self.assertEqual(r.returncode, 0)
        self.assertIn("WARNING", r.stderr)


class TestRetirementProjection(unittest.TestCase):
    """lifestyle/personal-finance/scripts/retirement-projection.py"""

    SCRIPT = "lifestyle/personal-finance/scripts/retirement-projection.py"

    def test_sustained_scenario(self):
        r = run(self.SCRIPT,
                "--age", "35", "--retire", "65",
                "--super", "120000", "--salary", "110000",
                "--contrib_pct", "0.115", "--return", "0.07",
                "--inflation", "0.025", "--drawdown_pct", "0.04",
                "--years_drawdown", "25")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Nominal:", r.stdout)
        self.assertIn("Outcome:", r.stdout)

    def test_depleted_scenario(self):
        # Tiny balance + high drawdown should deplete quickly
        r = run(self.SCRIPT,
                "--age", "65", "--retire", "66",
                "--super", "50000", "--salary", "60000",
                "--contrib_pct", "0.115", "--return", "0.04",
                "--inflation", "0.025", "--drawdown_pct", "0.20",
                "--years_drawdown", "25")
        self.assertEqual(r.returncode, 0)
        self.assertIn("depleted", r.stdout)


class TestDebtPayoffCalc(unittest.TestCase):
    """lifestyle/personal-finance/scripts/debt-payoff-calc.py"""

    SCRIPT = "lifestyle/personal-finance/scripts/debt-payoff-calc.py"

    def _make_csv(self) -> str:
        return (
            "name,balance,apr,min_payment\n"
            "CC1,5000,0.21,150\n"
            "Personal,8000,0.10,200\n"
            "Car,12000,0.08,350\n"
        )

    def test_both_strategies(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(self._make_csv())
            path = f.name
        try:
            r = run(self.SCRIPT, "--csv", path, "--extra_monthly", "500",
                    "--strategy", "both")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Avalanche:", r.stdout)
            self.assertIn("Snowball:", r.stdout)
        finally:
            os.unlink(path)

    def test_avalanche_only(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(self._make_csv())
            path = f.name
        try:
            r = run(self.SCRIPT, "--csv", path, "--extra_monthly", "300",
                    "--strategy", "avalanche")
            self.assertEqual(r.returncode, 0)
            self.assertIn("Avalanche", r.stdout)
            self.assertNotIn("Snowball", r.stdout)
        finally:
            os.unlink(path)


class TestPowerCalc(unittest.TestCase):
    """data-science/experimentation/scripts/power-calc.py"""

    SCRIPT = "data-science/experimentation/scripts/power-calc.py"

    def test_standard_ab_test(self):
        r = run(self.SCRIPT, "--baseline", "0.05", "--mde", "0.005",
                "--alpha", "0.05", "--power", "0.8", "--two_sided")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Sample per group:", r.stdout)
        self.assertIn("Total sample:", r.stdout)

    def test_smaller_mde_needs_more_sample(self):
        r1 = run(self.SCRIPT, "--baseline", "0.10", "--mde", "0.01", "--two_sided")
        r2 = run(self.SCRIPT, "--baseline", "0.10", "--mde", "0.005", "--two_sided")
        # Extract numbers
        def n_from(out):
            for line in out.splitlines():
                if "Total sample:" in line:
                    return int(line.split(":")[1].strip().replace(",", ""))
            return None
        n1 = n_from(r1.stdout)
        n2 = n_from(r2.stdout)
        self.assertGreater(n2, n1, "smaller MDE should require more sample")


class TestCvpCalc(unittest.TestCase):
    """economics/business-economics/scripts/cvp-calc.py"""

    SCRIPT = "economics/business-economics/scripts/cvp-calc.py"

    def test_basic_break_even(self):
        r = run(self.SCRIPT, "--fixed", "100000", "--variable_per_unit", "20",
                "--price", "50", "--target_profit", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Break-even units:", r.stdout)
        self.assertIn("Sensitivity", r.stdout)

    def test_negative_margin_errors(self):
        r = run(self.SCRIPT, "--fixed", "100000", "--variable_per_unit", "60",
                "--price", "50", "--target_profit", "0")
        # cm_per_unit = 50 - 60 = -10; should print error and exit non-zero
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ERROR", r.stderr)


class TestLinkCheck(unittest.TestCase):
    """utilities/utilities/scripts/link-check.py — offline-only test (no network)"""

    SCRIPT = "utilities/utilities/scripts/link-check.py"

    def test_internal_links(self):
        # Create a small docs tree with one good + one bad internal link
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "index.md").write_text(
                "Good link: [exists](other.md)\n"
                "Bad link: [missing](does-not-exist.md)\n",
                encoding="utf-8",
            )
            (root / "other.md").write_text("# Other\n", encoding="utf-8")
            csv_path = root / "results.csv"
            r = run(self.SCRIPT, str(root), "--workers", "2",
                    "--csv", str(csv_path))
            # Script exits non-zero if any broken link found (expected here)
            self.assertIn(r.returncode, (0, 1))
            self.assertTrue(csv_path.exists())
            content = csv_path.read_text(encoding="utf-8")
            self.assertIn("does-not-exist.md", content)
            self.assertIn("other.md", content)


def _bash_available() -> bool:
    """Detect whether bash is directly invocable from this Python subprocess."""
    try:
        r = subprocess.run(["bash", "-c", "echo ok"], capture_output=True,
                           text=True, check=False, timeout=5)
        return r.returncode == 0 and "ok" in r.stdout
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return False


BASH_OK = _bash_available()


@unittest.skipUnless(BASH_OK, "bash not invocable from subprocess on this host")
class TestParseAuditReport(unittest.TestCase):
    """utilities/utilities/skills/audit-resolver/scripts/parse-audit-report.sh"""

    SCRIPT = "utilities/utilities/skills/audit-resolver/scripts/parse-audit-report.sh"

    def _run_with_report(self, content: str) -> subprocess.CompletedProcess:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            path = f.name
        try:
            return subprocess.run(
                ["bash", str(REPO_ROOT / self.SCRIPT), path],
                capture_output=True, text=True, check=False, timeout=15,
            )
        finally:
            os.unlink(path)

    def test_table_format_findings(self):
        report = """# Audit
## Phase 2: Type Safety
| ID | Severity | File:Line | Description |
|----|----------|-----------|-------------|
| 1 | CRITICAL | `src/foo.ts:42` | missing return type |
| 2 | WARNING | `src/bar.ts:9` | unused import |
"""
        r = self._run_with_report(report)
        self.assertEqual(r.returncode, 0, r.stderr)
        # TSV output: 2 findings
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        self.assertGreaterEqual(len(lines), 2)
        self.assertIn("CRITICAL", r.stdout)
        self.assertIn("WARNING", r.stdout)

    def test_bullet_format_findings(self):
        report = """# Audit
## Phase 8: Cleanup
- **W1:** `lifestyle/skills/x/SKILL.md:74` — dangling reference
- **C2:** `engineering/db/migration.sql:12` — missing index
"""
        r = self._run_with_report(report)
        self.assertEqual(r.returncode, 0)
        self.assertIn("WARNING", r.stdout)
        self.assertIn("CRITICAL", r.stdout)

    def test_empty_report_warns(self):
        report = "# Just a heading\n\nNo findings here.\n"
        r = self._run_with_report(report)
        # Script still exits 0 but emits WARNING on stderr
        self.assertEqual(r.returncode, 0)
        self.assertIn("WARNING", r.stderr)

    def test_missing_file_errors(self):
        r = subprocess.run(
            ["bash", str(REPO_ROOT / self.SCRIPT), "/does/not/exist.md"],
            capture_output=True, text=True, check=False, timeout=10,
        )
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not found", r.stderr.lower())


@unittest.skipUnless(BASH_OK, "bash not invocable from subprocess on this host")
class TestVerifyStack(unittest.TestCase):
    """utilities/utilities/skills/audit-resolver/scripts/verify-stack.sh"""

    SCRIPT = "utilities/utilities/skills/audit-resolver/scripts/verify-stack.sh"

    def test_detects_marketplace_stack_dry_run(self):
        # Run --dry-run from this repo root; should detect check-versions + smoke tests
        r = subprocess.run(
            ["bash", str(REPO_ROOT / self.SCRIPT), "--dry-run"],
            capture_output=True, text=True, check=False, timeout=15,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("check-versions.mjs", r.stdout)
        self.assertIn("dry-run", r.stdout.lower())

    def test_empty_dir_reports_no_verifiers(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(
                ["bash", str(REPO_ROOT / self.SCRIPT), "--dry-run"],
                capture_output=True, text=True, check=False, timeout=10,
                cwd=d,
            )
            # Empty dir: script exits 0 and emits "no verifiers detected" on stderr
            self.assertEqual(r.returncode, 0)
            self.assertIn("no verifiers detected", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
