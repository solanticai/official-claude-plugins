#!/usr/bin/env bash
# collect-open-questions.sh — List unresolved questions filed in .anthril/questions/.
# Usage: bash scripts/collect-open-questions.sh <project-root>
# Output: JSON to stdout, with shape:
#   {
#     "total": N,
#     "pending": [
#       { "agent": "frontend-auditor", "file": ".anthril/questions/frontend-auditor-1.md", "question": "...", "answered": false },
#       ...
#     ]
#   }
# Exit 0 iff total === 0; exit 2 if questions are pending; exit 1 on error.
#
# A question file is considered "answered" if its `## Answer` section contains
# anything other than "(awaiting answer)" or whitespace. Answered files are
# left in `.anthril/questions/` until /audit-proceed moves them to .resolved/.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
QUESTIONS_DIR="$PROJECT_ROOT/.anthril/questions"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo '{"total":0,"pending":[],"error":"target not a directory"}' >&2
  exit 1
fi

if [ ! -d "$QUESTIONS_DIR" ]; then
  echo '{"total":0,"pending":[]}'
  exit 0
fi

python3 - "$QUESTIONS_DIR" <<'PY'
import json, os, re, sys

qdir = sys.argv[1]
pending = []

for entry in sorted(os.listdir(qdir)):
    if not entry.endswith(".md"):
        continue
    full = os.path.join(qdir, entry)
    if not os.path.isfile(full):
        continue
    try:
        with open(full, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        continue

    # Agent name: <agent>-<n>.md
    m = re.match(r"^(.+?)-\d+\.md$", entry)
    agent = m.group(1) if m else "unknown"

    # Question: first non-empty line after `## Question`.
    qm = re.search(r"^##\s+Question\s*\n+(.+?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    question_text = (qm.group(1).strip() if qm else "").splitlines()[0] if qm else ""

    # Answer status: text after `## Answer` (excluding placeholder).
    am = re.search(r"^##\s+Answer\s*\n+(?:>[^\n]*\n+)*(.*?)\Z", text, re.MULTILINE | re.DOTALL)
    answer_body = (am.group(1).strip() if am else "")
    placeholder_re = re.compile(r"^\s*_?\(awaiting answer\)_?\s*$", re.IGNORECASE)
    answered = bool(answer_body) and not placeholder_re.match(answer_body) and answer_body.strip() != ""

    if not answered:
        # Use a relative path from project root for the report.
        rel = os.path.relpath(full, os.path.dirname(qdir.rstrip("/").rstrip("\\")) + "/..").replace("\\", "/")
        # Fallback: just print "questions/<entry>" if relpath gymnastics fail.
        if not rel.startswith(".anthril"):
            rel = ".anthril/questions/" + entry
        pending.append({
            "agent": agent,
            "file": rel,
            "question": question_text or "(no question text parsed)",
            "answered": False,
        })

result = {"total": len(pending), "pending": pending}
json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
sys.stdout.write("\n")

# Exit code: 0 if clean, 2 if questions pending.
sys.exit(2 if pending else 0)
PY
