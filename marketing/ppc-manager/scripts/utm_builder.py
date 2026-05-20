#!/usr/bin/env python3
"""UTM builder — pure Python, no API calls.

Takes a base URL and campaign parameters and produces one or more tagged URLs.
Supports single-URL mode and CSV batch mode.

Usage:
    python utm_builder.py build --url https://koalahomewares.com.au --source google --medium cpc --campaign winter
    python utm_builder.py batch --input campaigns.csv --output tagged.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

# Canonical naming rules
_NAME_RE = re.compile(r"^[a-z0-9_\-]+$")


def _normalise(value: str) -> str:
    """Lowercase + snake-case a value; strip any invalid chars."""
    value = value.strip().lower().replace(" ", "_").replace("-", "_")
    return re.sub(r"[^a-z0-9_]", "", value)


def build_utm_url(
    base_url: str,
    source: str,
    medium: str,
    campaign: str,
    term: Optional[str] = None,
    content: Optional[str] = None,
    id_: Optional[str] = None,
) -> str:
    """Append UTM parameters to a URL.

    All parameters are lowercased and snake_cased for consistency.
    """
    source = _normalise(source)
    medium = _normalise(medium)
    campaign = _normalise(campaign)

    params: Dict[str, str] = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    if term:
        params["utm_term"] = _normalise(term)
    if content:
        params["utm_content"] = _normalise(content)
    if id_:
        params["utm_id"] = id_

    parsed = urlparse(base_url)
    existing = dict(parse_qsl(parsed.query))
    existing.update(params)
    new_query = urlencode(existing)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )


def batch_from_csv(input_path: Path, output_path: Path) -> int:
    """Read a CSV of campaign rows and write an output CSV with tagged URLs.

    Expected input columns: url, source, medium, campaign, term (optional),
    content (optional), id (optional).
    """
    with input_path.open("r", encoding="utf-8", newline="") as in_fh:
        reader = csv.DictReader(in_fh)
        rows = list(reader)

    output_rows: List[Dict[str, Any]] = []
    for row in rows:
        tagged = build_utm_url(
            base_url=row["url"],
            source=row["source"],
            medium=row["medium"],
            campaign=row["campaign"],
            term=row.get("term") or None,
            content=row.get("content") or None,
            id_=row.get("id") or None,
        )
        output_rows.append({**row, "tagged_url": tagged})

    with output_path.open("w", encoding="utf-8", newline="") as out_fh:
        fieldnames = list(output_rows[0].keys()) if output_rows else []
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return len(output_rows)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ppc-manager UTM builder")
    sub = parser.add_subparsers(dest="mode", required=True)

    build_parser = sub.add_parser("build", help="Build a single tagged URL")
    build_parser.add_argument("--url", required=True)
    build_parser.add_argument("--source", required=True)
    build_parser.add_argument("--medium", required=True)
    build_parser.add_argument("--campaign", required=True)
    build_parser.add_argument("--term", default=None)
    build_parser.add_argument("--content", default=None)
    build_parser.add_argument("--id", dest="id_", default=None)

    batch_parser = sub.add_parser("batch", help="Build many tagged URLs from a CSV")
    batch_parser.add_argument("--input", type=Path, required=True)
    batch_parser.add_argument("--output", type=Path, required=True)

    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.mode == "build":
        url = build_utm_url(
            base_url=args.url,
            source=args.source,
            medium=args.medium,
            campaign=args.campaign,
            term=args.term,
            content=args.content,
            id_=args.id_,
        )
        print(url)
        return 0
    if args.mode == "batch":
        count = batch_from_csv(args.input, args.output)
        print(f"Wrote {count} tagged URLs to {args.output}")
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
