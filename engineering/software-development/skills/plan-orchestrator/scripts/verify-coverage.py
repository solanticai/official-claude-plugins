#!/usr/bin/env python3
"""verify-coverage.py — Confirm every input task ID appears in the assembled
sub-agent report buffer.

Inputs:
  --tasks <path>   Path to the tasks JSON (output of classify-tasks.py or
                   parse-bullets.py — anything with a top-level `tasks` array
                   of objects with an `id` field).
  stdin            The concatenated report buffer (raw markdown).

Outputs:
  stdout           A JSON object:
                     {
                       "covered":     ["T1", "T2", ...],
                       "missing":     ["T3"],
                       "duplicates":  ["T1"],
                       "spurious":    [],
                       "coverage_pct": 80.0
                     }
  exit code        0 iff missing == [] and spurious == []. 1 otherwise.

Heading-detection rule (load-bearing — see reference.md §4):
  A task ID T<N> is considered covered if the buffer contains a line matching:
      ^###\\s+(T\\d+)\\b
  Anything that doesn't match that pattern is invisible to the verifier,
  even if the ID appears elsewhere in the body.

Spurious IDs (T<N> headings that weren't in the input task list) are also
flagged — this catches an agent that hallucinates a task.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

HEADING_RE = re.compile(r"^###\s+(T\d+)\b", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify task coverage in agent reports.")
    parser.add_argument("--tasks", required=True, help="Path to tasks JSON")
    args = parser.parse_args()

    with open(args.tasks, "r", encoding="utf-8") as f:
        payload = json.load(f)
    expected_ids = [t["id"] for t in payload.get("tasks", [])]

    buffer = sys.stdin.read()
    found_ids = HEADING_RE.findall(buffer)

    expected_set = set(expected_ids)
    found_counter: dict[str, int] = {}
    for tid in found_ids:
        found_counter[tid] = found_counter.get(tid, 0) + 1

    covered = [tid for tid in expected_ids if tid in found_counter]
    missing = [tid for tid in expected_ids if tid not in found_counter]
    duplicates = sorted({tid for tid, n in found_counter.items() if n > 1 and tid in expected_set})
    spurious = sorted({tid for tid in found_counter if tid not in expected_set})

    coverage_pct = (len(covered) / len(expected_ids) * 100) if expected_ids else 0.0

    result = {
        "covered": covered,
        "missing": missing,
        "duplicates": duplicates,
        "spurious": spurious,
        "coverage_pct": round(coverage_pct, 2),
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")

    return 0 if not missing and not spurious else 1


if __name__ == "__main__":
    sys.exit(main())
