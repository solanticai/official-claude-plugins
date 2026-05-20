#!/usr/bin/env python3
"""parse-bullets.py — Parse a multi-line bullet list from stdin into a JSON task list.

Input (stdin): the raw $ARGUMENTS block from the slash command, e.g.:

    target: ./apps/web

    * Add a sign-out button to the user menu
    - Fix the 500 on /api/orders when cart is empty
    1. Migrate the orders table to add a `currency` column
    * Bug: stripe webhook doesn't verify signatures

Output (stdout): a JSON object:
    {
      "target": "./apps/web" | null,
      "tasks": [
        {"id": "T1", "text": "Add a sign-out button to the user menu"},
        {"id": "T2", "text": "Fix the 500 on /api/orders when cart is empty"},
        ...
      ],
      "count": 4
    }

Bullet syntaxes recognised:
  *   item
  -   item
  1.  item
  1)  item
  •   item

Lines that don't match a bullet pattern are ignored, EXCEPT a leading
'target: <path>' line which is captured into the `target` field.

Empty input (or input with zero recognised bullets) returns
    {"target": null, "tasks": [], "count": 0}
and exits 0 — the caller decides what to do.
"""

from __future__ import annotations

import json
import re
import sys

# Match leading bullet markers; capture the remaining text.
BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.*\S)\s*$")
TARGET_RE = re.compile(r"^\s*target\s*:\s*(\S.*\S|\S)\s*$", re.IGNORECASE)


def parse(stream: str) -> dict:
    target: str | None = None
    tasks: list[dict] = []
    next_id = 1

    for raw_line in stream.splitlines():
        if not raw_line.strip():
            continue

        # Capture an optional 'target: <path>' on its own line.
        if target is None:
            m_target = TARGET_RE.match(raw_line)
            if m_target:
                target = m_target.group(1).strip()
                continue

        m_bullet = BULLET_RE.match(raw_line)
        if not m_bullet:
            continue

        text = m_bullet.group(1).strip()
        # Drop empty bullets like "* "
        if not text:
            continue

        tasks.append({"id": f"T{next_id}", "text": text})
        next_id += 1

    return {"target": target, "tasks": tasks, "count": len(tasks)}


def main() -> int:
    raw = sys.stdin.read()
    result = parse(raw)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
