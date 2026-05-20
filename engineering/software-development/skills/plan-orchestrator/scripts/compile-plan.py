#!/usr/bin/env python3
"""compile-plan.py — Compile sub-agent reports into a single ordered plan.

Inputs:
  --tasks   <path>      Path to the tasks JSON (with `tasks` array, each having
                        id, text, domains).
  --reports <path>      Path to the concatenated sub-agent report buffer
                        (raw markdown). The buffer is expected to contain
                        per-task sections of the form:
                          ### T<N> — <title>
                          **Original:** ...
                          **Domain:** ...
                          ... freeform body ...
  --coverage <path>     Path to the JSON output of verify-coverage.py.

Output (stdout):  the rendered final plan, in markdown, following the
                  structure defined in templates/plan-template.md and
                  reference.md §6.

Determinism:  the plan section order is fixed (Run header → Coverage table
              → Per-task blocks in input order → File aggregation →
              Cross-cutting → Execution order → Unresolved). Two runs over
              identical inputs produce byte-identical output.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict, OrderedDict

# Section delimiter in the report buffer. Captures the task ID and the section
# body up to the next per-task heading, the next top-level/second-level heading
# (catches agent boundaries like '# Agent Report — backend-investigator'), or
# end-of-buffer — whichever comes first.
SECTION_RE = re.compile(
    r"^###\s+(T\d+)\b[^\n]*\n(?P<body>.*?)(?=^###\s+T\d+\b|^#{1,2}\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)

# Inside a section body, find file references like `path/to/file.ext:42`
# or `path/to/file.ext` inside backticks. Captures the file portion only.
FILE_REF_RE = re.compile(
    r"`([A-Za-z0-9_./\-]+\.[A-Za-z0-9]+)(?::\d+)?`"
)

# Whitelist of extensions we treat as actual file references. Anything in
# backticks that has a dot but no `/` and an unrecognised extension is more
# likely an identifier (`public.orders`, `stripe.webhooks.constructEvent`)
# than a file. Paths containing `/` are accepted regardless of extension.
FILE_EXTENSIONS = frozenset({
    # JS/TS
    "ts", "tsx", "js", "jsx", "mjs", "cjs", "vue", "svelte", "astro",
    # Python
    "py", "pyi", "pyx",
    # Other languages
    "go", "rs", "java", "kt", "kts", "scala", "rb", "php", "cs", "fs",
    "swift", "m", "mm", "c", "cc", "cpp", "h", "hpp", "ex", "exs", "erl",
    "lua", "dart", "clj", "cljs", "r", "pl", "pm",
    # Data / config / docs
    "json", "jsonc", "yaml", "yml", "toml", "ini", "conf", "xml",
    "md", "mdx", "rst", "txt", "csv", "tsv", "env",
    # Web
    "html", "htm", "css", "scss", "sass", "less",
    # SQL / schema
    "sql", "prisma", "graphql", "gql", "proto",
    # Shell / build
    "sh", "bash", "zsh", "fish", "ps1", "lock", "make", "mk",
    # Container / infra
    "dockerfile", "tf", "tfvars", "nix",
})


def _is_file_path(path: str) -> bool:
    """Heuristic: treat a backtick-wrapped value as a file iff it either
    contains a path separator or ends with a recognised file extension."""
    if "/" in path or "\\" in path:
        return True
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return ext in FILE_EXTENSIONS


def parse_sections(buffer: str) -> "OrderedDict[str, list[str]]":
    """Return an OrderedDict mapping task_id -> list of section bodies
    (one per agent that addressed that task)."""
    sections: "OrderedDict[str, list[str]]" = OrderedDict()
    for m in SECTION_RE.finditer(buffer):
        tid = m.group(1)
        body = m.group("body").strip()
        # Drop trailing `---` separator lines (and any blank lines after them)
        # so visual separators between agent reports don't render as junk.
        body = re.sub(r"(\n[\s]*-{3,}[\s]*)+\s*$", "", body).rstrip()
        sections.setdefault(tid, []).append(body)
    return sections


def extract_files(body: str) -> set[str]:
    return {p for p in FILE_REF_RE.findall(body) if _is_file_path(p)}


def render_coverage_marker(tid: str, coverage: dict) -> str:
    if tid in coverage.get("missing", []):
        return "🔴 missing"
    if tid in coverage.get("duplicates", []):
        return "🟡 duplicate"
    if tid in coverage.get("covered", []):
        return "🟢 covered"
    return "⚪ unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile multi-agent reports into one plan.")
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--reports", required=True)
    parser.add_argument("--coverage", required=True)
    args = parser.parse_args()

    with open(args.tasks, "r", encoding="utf-8") as f:
        tasks_payload = json.load(f)
    with open(args.reports, "r", encoding="utf-8") as f:
        reports_buffer = f.read()
    with open(args.coverage, "r", encoding="utf-8") as f:
        coverage = json.load(f)

    tasks = tasks_payload.get("tasks", [])
    target = tasks_payload.get("target") or "(working directory)"
    routing = tasks_payload.get("routing", {})
    sections = parse_sections(reports_buffer)

    out = []

    # 1. Run header
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    out.append("# Plan Orchestrator — Consolidated Plan\n")
    out.append("| Field | Value |")
    out.append("|---|---|")
    out.append(f"| **Generated** | {now} |")
    out.append(f"| **Target** | `{target}` |")
    out.append(f"| **Tasks** | {len(tasks)} |")
    out.append(f"| **Domains routed** | {len(routing)} |")
    out.append(f"| **Coverage** | {coverage.get('coverage_pct', 0)}% "
               f"(missing: {len(coverage.get('missing', []))}, "
               f"spurious: {len(coverage.get('spurious', []))}) |")
    out.append("")

    # 2. Task coverage table
    out.append("## 1. Task Coverage")
    out.append("")
    out.append("| ID | Status | Domains | Original task |")
    out.append("|---|---|---|---|")
    for task in tasks:
        marker = render_coverage_marker(task["id"], coverage)
        domains = ", ".join(task.get("domains", [])) or "—"
        # Escape pipes in user text so the table doesn't break.
        text = task["text"].replace("|", "\\|")
        out.append(f"| {task['id']} | {marker} | {domains} | {text} |")
    out.append("")

    # 3. Per-task plan blocks (in original input order)
    out.append("## 2. Per-Task Plan")
    out.append("")
    for task in tasks:
        tid = task["id"]
        out.append(f"### {tid} — {task['text']}")
        out.append("")
        out.append(f"**Domains:** {', '.join(task.get('domains', []))}")
        bodies = sections.get(tid, [])
        if not bodies:
            out.append("")
            out.append("> ⚠️ **UNRESOLVED — investigate manually.** "
                       "No sub-agent returned a section for this task ID.")
            out.append("")
            continue
        if len(bodies) > 1:
            out.append(f"**Contributing agents:** {len(bodies)}")
        out.append("")
        for i, body in enumerate(bodies, 1):
            if len(bodies) > 1:
                out.append(f"#### Contribution {i}")
                out.append("")
            out.append(body.rstrip())
            out.append("")

    # 4. Aggregated change set by file
    file_to_tasks: dict[str, list[str]] = defaultdict(list)
    for tid, bodies in sections.items():
        files: set[str] = set()
        for body in bodies:
            files |= extract_files(body)
        for fpath in files:
            file_to_tasks[fpath].append(tid)
    if file_to_tasks:
        out.append("## 3. Aggregated Change Set by File")
        out.append("")
        out.append("Files referenced across the per-task plans, sorted alphabetically. "
                   "If multiple tasks touch the same file, batch the changes.")
        out.append("")
        out.append("| File | Tasks |")
        out.append("|---|---|")
        for fpath in sorted(file_to_tasks):
            tids = sorted(set(file_to_tasks[fpath]),
                          key=lambda x: int(x[1:]))
            out.append(f"| `{fpath}` | {', '.join(tids)} |")
        out.append("")

    # 5. Cross-cutting concerns (tasks that ended up in 2+ domains)
    cross = [t for t in tasks if len(t.get("domains", [])) > 1]
    if cross:
        out.append("## 4. Cross-Cutting Concerns")
        out.append("")
        out.append("Tasks that span multiple domains. Coordinate the relevant agents' "
                   "recommendations in your execution.")
        out.append("")
        for task in cross:
            out.append(f"- **{task['id']}** ({', '.join(task['domains'])}) — {task['text']}")
        out.append("")

    # 6. Suggested execution order
    DOMAIN_ORDER = ["database", "infrastructure", "security", "backend",
                    "frontend", "testing", "documentation"]
    grouped: "OrderedDict[str, list[str]]" = OrderedDict((d, []) for d in DOMAIN_ORDER)
    for task in tasks:
        # Pick the highest-priority domain for ordering (lowest index in DOMAIN_ORDER).
        primary = min(
            (d for d in task.get("domains", []) if d in grouped),
            key=lambda d: DOMAIN_ORDER.index(d),
            default=None,
        )
        if primary:
            grouped[primary].append(task["id"])
    out.append("## 5. Suggested Execution Order")
    out.append("")
    out.append("Apply changes in this order to minimise rework: schema → infra → "
               "security → backend → frontend → tests → docs.")
    out.append("")
    step = 1
    for domain, ids in grouped.items():
        if not ids:
            continue
        out.append(f"{step}. **{domain.capitalize()}** — {', '.join(ids)}")
        step += 1
    out.append("")

    # 7. Unresolved items
    missing = coverage.get("missing", [])
    if missing:
        out.append("## 6. Unresolved Items")
        out.append("")
        out.append("These task IDs did not receive coverage from any sub-agent, even after "
                   "sweeper rounds. Investigate manually before acting on the plan.")
        out.append("")
        id_to_text = {t["id"]: t["text"] for t in tasks}
        for tid in missing:
            out.append(f"- **{tid}** — {id_to_text.get(tid, '(unknown)')}")
        out.append("")

    sys.stdout.write("\n".join(out))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
