#!/usr/bin/env python3
"""macro-calc.py — TDEE + macro split helper for week-of-meals.

Usage:
  python macro-calc.py --sex M --age 34 --kg 80 --cm 178 --activity 1.55 --goal recomp

No network. Pure stdlib.

Mifflin-St Jeor BMR:
  M: 10*kg + 6.25*cm - 5*age + 5
  F: 10*kg + 6.25*cm - 5*age - 161

Activity multipliers:
  sedentary (desk + minimal exercise):   1.2
  light    (light exercise 1-3 days):    1.375
  moderate (moderate exercise 3-5 days): 1.55
  active   (hard exercise 6-7 days):     1.725
  very     (athlete + physical job):     1.9

Goal adjustments (kcal/day):
  maintenance: +0
  recomp:      +200
  hypertrophy: +400
  loss:        -400
  agg_loss:    -600  (warns and recommends GP)

Macro defaults:
  protein g/kg: 1.6 (maintenance), 1.8 (loss), 2.0 (recomp/hypertrophy)
  fat g/kg:     0.9
  carbs:        remainder
"""
from __future__ import annotations

import argparse
import sys


def bmr_mifflin(sex: str, kg: float, cm: float, age: int) -> float:
    base = 10 * kg + 6.25 * cm - 5 * age
    return base + 5 if sex.upper() == "M" else base - 161


GOAL_ADJ = {
    "maintenance": 0,
    "recomp": 200,
    "hypertrophy": 400,
    "loss": -400,
    "agg_loss": -600,
}

PROTEIN_PER_KG = {
    "maintenance": 1.6,
    "recomp": 2.0,
    "hypertrophy": 2.0,
    "loss": 1.8,
    "agg_loss": 2.2,
}


def compute(sex: str, age: int, kg: float, cm: float, activity: float, goal: str) -> dict:
    bmr = bmr_mifflin(sex, kg, cm, age)
    tdee = bmr * activity
    target = tdee + GOAL_ADJ[goal]
    protein_g = round(PROTEIN_PER_KG[goal] * kg)
    fat_g = round(0.9 * kg)
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    carb_kcal = target - protein_kcal - fat_kcal
    carbs_g = round(max(carb_kcal, 0) / 4)
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_kcal": round(target),
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carbs_g": carbs_g,
        "warning": "aggressive deficit — recommend GP/APD supervision" if goal == "agg_loss" else None,
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="TDEE + macro split helper")
    p.add_argument("--sex", required=True, choices=["M", "F", "m", "f"])
    p.add_argument("--age", type=int, required=True)
    p.add_argument("--kg", type=float, required=True)
    p.add_argument("--cm", type=float, required=True)
    p.add_argument("--activity", type=float, default=1.55,
                   help="1.2 sedentary, 1.375 light, 1.55 moderate, 1.725 active, 1.9 very")
    p.add_argument("--goal", default="maintenance", choices=list(GOAL_ADJ.keys()))
    args = p.parse_args(argv)
    out = compute(args.sex, args.age, args.kg, args.cm, args.activity, args.goal)
    print(f"BMR:       {out['bmr']:>5} kcal")
    print(f"TDEE:      {out['tdee']:>5} kcal")
    print(f"Target:    {out['target_kcal']:>5} kcal")
    print(f"Protein:   {out['protein_g']:>5} g")
    print(f"Fat:       {out['fat_g']:>5} g")
    print(f"Carbs:     {out['carbs_g']:>5} g")
    if out["warning"]:
        print(f"\nWARNING: {out['warning']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
