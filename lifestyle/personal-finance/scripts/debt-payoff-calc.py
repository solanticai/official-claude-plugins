#!/usr/bin/env python3
"""debt-payoff-calc.py — Avalanche vs snowball debt payoff timeline.

Pure stdlib. Reads debts from a CSV path or stdin in the form:
  name,balance,apr,min_payment

Usage:
  python debt-payoff-calc.py --csv debts.csv --extra_monthly 500 --strategy both
"""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Iterable


def parse_debts(rows: Iterable[dict]) -> list[dict]:
    debts = []
    for r in rows:
        debts.append({
            "name": r["name"].strip(),
            "balance": float(r["balance"]),
            "apr": float(r["apr"]),  # e.g. 0.205 for 20.5%
            "min_payment": float(r["min_payment"]),
        })
    return debts


def simulate(debts: list[dict], extra_monthly: float, strategy: str) -> dict:
    debts = [dict(d) for d in debts]
    if strategy == "avalanche":
        order_key = lambda d: -d["apr"]
    else:  # snowball
        order_key = lambda d: d["balance"]
    month = 0
    total_interest = 0.0
    timeline = []
    while any(d["balance"] > 0.01 for d in debts) and month < 360:
        month += 1
        for d in debts:
            if d["balance"] <= 0:
                continue
            interest = d["balance"] * d["apr"] / 12
            d["balance"] += interest
            total_interest += interest
            pay = min(d["min_payment"], d["balance"])
            d["balance"] -= pay
        remaining_active = [d for d in debts if d["balance"] > 0.01]
        remaining_active.sort(key=order_key)
        budget = extra_monthly
        for d in remaining_active:
            if budget <= 0:
                break
            pay = min(budget, d["balance"])
            d["balance"] -= pay
            budget -= pay
        timeline.append((month, round(sum(d["balance"] for d in debts), 2)))
    return {
        "months": month,
        "total_interest": round(total_interest, 2),
        "timeline": timeline,
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", help="CSV path; columns: name,balance,apr,min_payment")
    p.add_argument("--extra_monthly", type=float, default=0)
    p.add_argument("--strategy", choices=["avalanche", "snowball", "both"], default="both")
    a = p.parse_args(argv)
    if a.csv:
        with open(a.csv, encoding="utf-8") as f:
            debts = parse_debts(csv.DictReader(f))
    else:
        debts = parse_debts(csv.DictReader(sys.stdin))

    if a.strategy in ("avalanche", "both"):
        out = simulate(debts, a.extra_monthly, "avalanche")
        print(f"Avalanche: payoff in {out['months']} months, total interest ${out['total_interest']:,}")
    if a.strategy in ("snowball", "both"):
        out = simulate(debts, a.extra_monthly, "snowball")
        print(f"Snowball:  payoff in {out['months']} months, total interest ${out['total_interest']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
