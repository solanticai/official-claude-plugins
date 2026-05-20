#!/usr/bin/env python3
"""classify-tasks.py — Tag each parsed task with one or more domain labels.

Input (stdin): the JSON output of parse-bullets.py.

Output (stdout): the same JSON augmented with a `domains` array per task,
plus an aggregate `routing` map at the top level:

    {
      "target": "...",
      "tasks": [
        {"id": "T1", "text": "...", "domains": ["frontend"], "default_tagged": false},
        {"id": "T2", "text": "...", "domains": ["database", "backend"], ...},
        ...
      ],
      "routing": {
        "frontend": ["T1"],
        "database": ["T2"],
        "backend":  ["T2", "T5"]
      },
      "agent_count_estimate": 3
    }

Heuristic: case-insensitive substring match against keyword lists per domain.
Tasks that match no keywords get `domains: ["backend"]` and `default_tagged: true`
so the orchestrator can flag the assumption to the user.

The classifier is deliberately simple. Sub-agents apply the real judgement.
"""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict

# Keep this list aligned with reference.md §1.
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "frontend": [
        "button", "page", "component", "style", "css", "tailwind",
        "react", "vue", "svelte", "next.js", "nextjs", "form", "modal",
        "responsive", "a11y", "accessibility", "lighthouse", "ui ", "ux ",
        "layout", "menu", "navbar", "sidebar", "icon", "animation",
        "tsx", "jsx", "client", "browser", "dom",
    ],
    "backend": [
        "api", "endpoint", "route", "handler", "service", "controller",
        "validation", "queue", "worker", "cron", "webhook", "rpc call",
        "middleware", "server action", "edge function", "serverless",
        "graphql", "rest", "fetch", "request", "response",
    ],
    "database": [
        "table", "column", "schema", "migration", "rls", "policy",
        "index", "query", " rpc", "trigger", "supabase", "postgres",
        "prisma", "drizzle", "typeorm", "sqlalchemy", "sql", "database",
        "db ", " db,", "row level security",
        # Note: bare SQL action verbs (select/insert/update/delete) are
        # deliberately omitted — they false-match common English verbs.
        # Real DB tasks reliably mention table/column/migration/query/etc.
    ],
    "infrastructure": [
        " ci", "cd ", "ci/cd", "deploy", "docker", "github action",
        "vercel", "cloudflare", "env ", "env var", " env,", "secret",
        " log,", "logging", "monitor", "alert", "sentry", "datadog",
        "grafana", "k8s", "kubernetes", "terraform", "wrangler",
    ],
    "testing": [
        " test", "tests", " spec", "specs", "unit ", "e2e",
        "playwright", "cypress", "jest", "vitest", "fixture", "mock",
        "coverage", "regression", "snapshot test",
    ],
    "security": [
        "auth ", "authn", "authz", "permission", "rbac", "csrf",
        " xss", " sqli", "injection", "secret", "token", "vulnerability",
        " cve", " audit", "sanitis", "sanitiz", "ssrf", "rate limit",
        "private key", "api key",
    ],
    "documentation": [
        "readme", "docs ", " docs,", "documentation", "comment",
        "jsdoc", "tsdoc", "changelog", "adr", "wiki", "runbook",
        "diagram", "explainer",
    ],
}

DEFAULT_DOMAIN = "backend"
MAX_PARALLEL_AGENTS = 8


def _normalise(text: str) -> str:
    """Lowercase and collapse whitespace; pad with spaces so word-boundary
    keywords that include leading/trailing spaces match cleanly."""
    return " " + re.sub(r"\s+", " ", text.lower()) + " "


def classify_one(text: str) -> tuple[list[str], bool]:
    norm = _normalise(text)
    matched: list[str] = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in norm:
                matched.append(domain)
                break  # one match per domain is enough
    if matched:
        return (matched, False)
    return ([DEFAULT_DOMAIN], True)


def build_routing(tasks: list[dict]) -> "OrderedDict[str, list[str]]":
    """Domain -> ordered list of task IDs covering it."""
    routing: "OrderedDict[str, list[str]]" = OrderedDict()
    # Preserve a stable domain order to make output diffable.
    for domain in DOMAIN_KEYWORDS:
        routing[domain] = []
    for task in tasks:
        for domain in task["domains"]:
            routing[domain].append(task["id"])
    # Drop empty domains.
    return OrderedDict((d, ids) for d, ids in routing.items() if ids)


def estimate_agent_count(routing: "OrderedDict[str, list[str]]") -> int:
    """Number of parallel agents we'd dispatch given the routing.

    Each domain gets at least one agent. Domains with >8 tasks get split
    into ceil(n/8) workers. Hard cap is MAX_PARALLEL_AGENTS.
    """
    count = 0
    for ids in routing.values():
        n = len(ids)
        count += max(1, -(-n // 8))  # ceil division
    return min(count, MAX_PARALLEL_AGENTS)


def main() -> int:
    payload = json.load(sys.stdin)
    tasks = payload.get("tasks", [])

    for task in tasks:
        domains, default_tagged = classify_one(task["text"])
        task["domains"] = domains
        task["default_tagged"] = default_tagged

    routing = build_routing(tasks)
    payload["routing"] = routing
    payload["agent_count_estimate"] = estimate_agent_count(routing)

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
