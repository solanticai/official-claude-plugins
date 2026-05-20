#!/usr/bin/env python3
"""render-summary.py — Emit the JSON sidecar that mirrors REPORT.md structurally.

The validator already wrote `validation.json` matching templates/findings-schema.json.
This script copies it (with light enrichment — adds the `audit.generated_at` if missing
and ensures `audit.id` matches `--audit-id`) to `REPORT.json` so consumers always see
a matching sidecar next to REPORT.md.

Inputs:
  --validation <path>   Path to validation.json (validator output).
  --audit-id <id>       Audit ID for sanity check.
  --out <path>          Where to write REPORT.json.

Output: REPORT.json at --out.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--validation", required=True, type=Path)
    p.add_argument("--audit-id", required=True)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.validation.exists():
        print(f"ERROR: validation file missing: {args.validation}", file=sys.stderr)
        return 1

    payload = json.loads(args.validation.read_text(encoding="utf-8"))

    payload.setdefault("schema_version", "1.0.0")
    audit = payload.setdefault("audit", {})
    if not audit.get("id"):
        audit["id"] = args.audit_id
    elif audit["id"] != args.audit_id:
        # Caller-supplied id wins so REPORT.md and REPORT.json agree.
        print(
            f"WARN: validation.json audit.id={audit['id']!r} does not match "
            f"--audit-id={args.audit_id!r}; overriding to match the report.",
            file=sys.stderr,
        )
        audit["id"] = args.audit_id
    audit.setdefault("generated_at", dt.datetime.now().isoformat(timespec="seconds"))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
