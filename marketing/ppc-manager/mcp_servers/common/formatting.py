"""Consistent output formatting helpers for MCP tool handlers.

Every MCP tool returns a dict, so Claude sees structured data. But when a
skill displays that dict to the user we prefer consistent markdown. These
helpers live here so every MCP server produces similar shapes.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Sequence


def truncate(value: Any, max_len: int = 80) -> str:
    """Stringify ``value`` and ellipsise if longer than ``max_len``."""
    s = str(value)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def as_table(rows: Iterable[dict], columns: Sequence[str]) -> str:
    """Render a list of dicts as a GitHub-flavoured markdown table.

    Args:
        rows: Sequence of dicts.
        columns: Column order. Column keys that are missing from a row are
            rendered as empty cells.
    """
    rows = list(rows)
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    if not rows:
        return "\n".join([header, sep, "| " + " | ".join("(none)" for _ in columns) + " |"])
    body_lines: List[str] = []
    for row in rows:
        cells = [truncate(row.get(col, ""), 80) for col in columns]
        body_lines.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + body_lines)
