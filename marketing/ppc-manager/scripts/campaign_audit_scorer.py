#!/usr/bin/env python3
"""Grade common PPC audit heuristics on a 0-100 scale.

Takes a JSON payload of campaign metrics and returns a per-check score +
overall account health score. Used by `campaign-audit` skill to produce
consistent numerical findings.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Check:
    name: str
    score: int  # 0-100
    severity: str  # critical / warning / ok
    detail: str
    remediation: str


def _score(value: float, thresholds: Dict[str, float]) -> int:
    """Bin a numeric value into a 0-100 score using threshold dict.

    thresholds = {"great": X, "good": Y, "fair": Z, "poor": W}
    Above "great" = 100, between good/great = 80, between fair/good = 60,
    between poor/fair = 40, below poor = 20.
    """
    if value >= thresholds["great"]:
        return 100
    if value >= thresholds["good"]:
        return 80
    if value >= thresholds["fair"]:
        return 60
    if value >= thresholds["poor"]:
        return 40
    return 20


def check_ctr(ctr: float) -> Check:
    """CTR check. Expect ≥2% for search."""
    score = _score(ctr, {"great": 4.0, "good": 2.5, "fair": 1.5, "poor": 0.8})
    severity = (
        "ok" if score >= 80 else "warning" if score >= 40 else "critical"
    )
    return Check(
        name="CTR",
        score=score,
        severity=severity,
        detail=f"CTR = {ctr:.2f}% (target ≥2.5%)",
        remediation=(
            "Improve ad relevance — check keyword/ad pairing, add more specific headlines."
            if score < 60
            else "Maintain current creative; review monthly."
        ),
    )


def check_cpa(cpa_aud: float, target_cpa_aud: float) -> Check:
    """CPA vs target CPA."""
    if cpa_aud <= 0 or target_cpa_aud <= 0:
        return Check("CPA", 0, "critical", "No conversions or target CPA unset", "Set a target CPA")
    ratio = target_cpa_aud / cpa_aud
    score = _score(ratio, {"great": 1.2, "good": 1.0, "fair": 0.75, "poor": 0.5})
    severity = "ok" if score >= 80 else "warning" if score >= 40 else "critical"
    return Check(
        name="CPA",
        score=score,
        severity=severity,
        detail=f"CPA = ${cpa_aud:.2f} vs target ${target_cpa_aud:.2f}",
        remediation=(
            "Reduce wasted spend via negative keywords; consider bid strategy change."
            if score < 60
            else "CPA is within acceptable range."
        ),
    )


def check_roas(roas: float) -> Check:
    """ROAS check. Expect ≥3.0 for e-commerce."""
    score = _score(roas, {"great": 5.0, "good": 3.0, "fair": 2.0, "poor": 1.0})
    severity = "ok" if score >= 80 else "warning" if score >= 40 else "critical"
    return Check(
        name="ROAS",
        score=score,
        severity=severity,
        detail=f"ROAS = {roas:.2f} (target ≥3.0)",
        remediation=(
            "Review bidding strategy, reduce low-margin SKUs, or pause worst performers."
            if score < 60
            else "ROAS is healthy."
        ),
    )


def check_wasted_spend_ratio(wasted: float, total: float) -> Check:
    """Wasted spend on queries without conversions / total spend."""
    if total <= 0:
        return Check("Wasted spend", 100, "ok", "No spend", "—")
    ratio = wasted / total
    score = _score(1 - ratio, {"great": 0.95, "good": 0.85, "fair": 0.70, "poor": 0.50})
    severity = "ok" if score >= 80 else "warning" if score >= 40 else "critical"
    return Check(
        name="Wasted spend",
        score=score,
        severity=severity,
        detail=f"${wasted:.2f} wasted on non-converting queries ({ratio*100:.0f}% of spend)",
        remediation=(
            "Add negative keywords from non-converting search terms report."
            if score < 80
            else "Acceptable."
        ),
    )


def check_conversion_count(conversions: int) -> Check:
    """Conversion volume for optimisation."""
    score = _score(float(conversions), {"great": 100, "good": 50, "fair": 30, "poor": 10})
    severity = "ok" if score >= 80 else "warning" if score >= 40 else "critical"
    return Check(
        name="Conversion volume",
        score=score,
        severity=severity,
        detail=f"{conversions} conversions in last 30 days",
        remediation=(
            "Too low for Smart Bidding. Use Manual CPC + Enhanced CPC until >30."
            if conversions < 30
            else "Sufficient for most bidding strategies."
        ),
    )


def audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Score every available metric and return a per-check + overall summary."""
    checks: List[Check] = []

    if "ctr" in payload:
        checks.append(check_ctr(float(payload["ctr"])))
    if "cpa_aud" in payload and "target_cpa_aud" in payload:
        checks.append(check_cpa(float(payload["cpa_aud"]), float(payload["target_cpa_aud"])))
    if "roas" in payload:
        checks.append(check_roas(float(payload["roas"])))
    if "wasted_spend_aud" in payload and "total_spend_aud" in payload:
        checks.append(
            check_wasted_spend_ratio(
                float(payload["wasted_spend_aud"]),
                float(payload["total_spend_aud"]),
            )
        )
    if "conversions_30d" in payload:
        checks.append(check_conversion_count(int(payload["conversions_30d"])))

    if not checks:
        return {"error": "No checks could be run", "checks": []}

    overall = sum(c.score for c in checks) // len(checks)
    return {
        "overall_score": overall,
        "checks": [
            {
                "name": c.name,
                "score": c.score,
                "severity": c.severity,
                "detail": c.detail,
                "remediation": c.remediation,
            }
            for c in checks
        ],
    }


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ppc-manager campaign audit scorer")
    parser.add_argument("--input", type=Path, required=True, help="JSON file with metrics")
    parser.add_argument("--output", type=Path, default=None, help="JSON output (default: stdout)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit(payload)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
