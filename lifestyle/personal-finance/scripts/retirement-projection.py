#!/usr/bin/env python3
"""retirement-projection.py — Compound growth + AU super accumulation + drawdown.

Pure stdlib. No network. Illustrative only — not financial advice.

Usage:
  python retirement-projection.py --age 35 --retire 65 --super 120000 --salary 110000 \
                                  --contrib_pct 0.115 --return 0.07 --inflation 0.025 \
                                  --drawdown_pct 0.04 --years_drawdown 25
"""
from __future__ import annotations

import argparse
import sys


def project(
    age: int,
    retire_age: int,
    super_balance: float,
    salary: float,
    contrib_pct: float,
    annual_return: float,
    inflation: float,
    drawdown_pct: float,
    years_drawdown: int,
) -> dict:
    years_accum = retire_age - age
    real_return = (1 + annual_return) / (1 + inflation) - 1
    balance = super_balance
    contrib_today = salary * contrib_pct
    history_accum = []
    for y in range(1, years_accum + 1):
        contrib = contrib_today * ((1 + inflation) ** y)
        balance = balance * (1 + annual_return) + contrib
        history_accum.append((age + y, round(balance), round(balance / ((1 + inflation) ** y))))
    nominal_at_retire = balance
    real_at_retire = balance / ((1 + inflation) ** years_accum)
    first_year_income = real_at_retire * drawdown_pct
    drawdown_history = []
    db = balance
    for y in range(1, years_drawdown + 1):
        spend = first_year_income * ((1 + inflation) ** (years_accum + y))
        db = db * (1 + annual_return) - spend
        drawdown_history.append((retire_age + y, round(db), round(db / ((1 + inflation) ** (years_accum + y)))))
        if db < 0:
            return {
                "outcome": "depleted",
                "depleted_at_age": retire_age + y,
                "nominal_at_retire": round(nominal_at_retire),
                "real_at_retire": round(real_at_retire),
                "first_year_income": round(first_year_income),
                "accum_history": history_accum,
                "drawdown_history": drawdown_history,
            }
    return {
        "outcome": "sustained",
        "depleted_at_age": None,
        "nominal_at_retire": round(nominal_at_retire),
        "real_at_retire": round(real_at_retire),
        "first_year_income": round(first_year_income),
        "balance_end": round(db),
        "accum_history": history_accum,
        "drawdown_history": drawdown_history,
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--age", type=int, required=True)
    p.add_argument("--retire", type=int, required=True, dest="retire_age")
    p.add_argument("--super", type=float, required=True, dest="super_balance")
    p.add_argument("--salary", type=float, required=True)
    p.add_argument("--contrib_pct", type=float, default=0.115)
    p.add_argument("--return", type=float, default=0.07, dest="annual_return")
    p.add_argument("--inflation", type=float, default=0.025)
    p.add_argument("--drawdown_pct", type=float, default=0.04)
    p.add_argument("--years_drawdown", type=int, default=25)
    a = p.parse_args(argv)
    out = project(
        a.age, a.retire_age, a.super_balance, a.salary, a.contrib_pct,
        a.annual_return, a.inflation, a.drawdown_pct, a.years_drawdown,
    )
    print(f"At retirement (age {a.retire_age}):")
    print(f"  Nominal:        ${out['nominal_at_retire']:>12,}")
    print(f"  Real (today's): ${out['real_at_retire']:>12,}")
    print(f"  First-year drawdown (real): ${out['first_year_income']:>10,}")
    print(f"Outcome: {out['outcome']}")
    if out["outcome"] == "depleted":
        print(f"  Depleted at age {out['depleted_at_age']}")
    else:
        print(f"  Balance at end: ${out['balance_end']:>12,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
