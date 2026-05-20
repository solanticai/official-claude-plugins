#!/usr/bin/env python3
"""link-check.py — Find broken links in markdown files.

Pure stdlib — uses urllib only (no `requests` dependency).

Usage:
  python link-check.py path/to/docs

Behaviour:
  - Recursively scans .md files
  - Extracts [text](url) links
  - Checks external HTTP/HTTPS links via HEAD (falls back to GET on 405)
  - Checks internal links (relative paths) by file existence
  - Skips mailto:, tel:, anchor-only (#section)
  - Outputs CSV: file,line,link,status,reason

Concurrency: simple thread-pool of 8 workers (avoids the requirement of asyncio).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Iterable

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
TIMEOUT = 10.0


def walk_markdown(root: str) -> Iterable[str]:
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def find_links(path: str) -> list[tuple[int, str]]:
    """Return [(line_number, url), ...]."""
    links = []
    try:
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in LINK_RE.finditer(line):
                    url = m.group(2).strip()
                    if url.startswith(("mailto:", "tel:", "#")):
                        continue
                    if url.startswith("javascript:"):
                        continue
                    links.append((lineno, url))
    except UnicodeDecodeError:
        pass
    return links


def check_url(url: str) -> tuple[str, str]:
    if url.startswith(("http://", "https://")):
        return check_http(url)
    return ("internal", url)  # caller resolves relative-path internals


def check_http(url: str) -> tuple[str, str]:
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "doc-link-validator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return (str(resp.status), "")
    except urllib.error.HTTPError as e:
        if e.code == 405:
            # Many servers refuse HEAD; retry with GET (read only headers)
            try:
                req = urllib.request.Request(url, method="GET",
                                             headers={"User-Agent": "doc-link-validator/1.0",
                                                      "Range": "bytes=0-0"})
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    return (str(resp.status), "GET-fallback")
            except Exception as e2:
                return ("ERROR", str(e2))
        return (str(e.code), e.reason or "")
    except urllib.error.URLError as e:
        return ("ERROR", str(e.reason) if hasattr(e, "reason") else str(e))
    except Exception as e:
        return ("ERROR", repr(e))


def check_internal(base_dir: str, file_path: str, url: str) -> tuple[str, str]:
    # Strip anchor + query
    target = url.split("#")[0].split("?")[0]
    if not target:
        return ("200", "anchor-only-internal")
    candidate = os.path.normpath(os.path.join(os.path.dirname(file_path), target))
    if os.path.exists(candidate):
        return ("200", "")
    return ("404", f"file not found: {candidate}")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("root", help="Docs root (directory)")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--csv", help="Output CSV path (default: stdout)")
    a = p.parse_args(argv)

    if not os.path.isdir(a.root):
        print(f"ERROR: not a directory: {a.root}", file=sys.stderr)
        return 1

    all_links = []
    for file_path in walk_markdown(a.root):
        for lineno, url in find_links(file_path):
            all_links.append((file_path, lineno, url))

    if not all_links:
        print("No links found.", file=sys.stderr)
        return 0

    results = []

    def task(item):
        file_path, lineno, url = item
        if url.startswith(("http://", "https://")):
            status, reason = check_http(url)
        else:
            status, reason = check_internal(a.root, file_path, url)
        return (file_path, lineno, url, status, reason)

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for result in ex.map(task, all_links):
            results.append(result)

    out_fh = open(a.csv, "w", newline="", encoding="utf-8") if a.csv else sys.stdout
    writer = csv.writer(out_fh)
    writer.writerow(["file", "line", "link", "status", "reason"])
    for row in results:
        writer.writerow(row)
    if a.csv:
        out_fh.close()

    broken = [r for r in results if r[3] in ("ERROR", "404", "403", "410") or r[3].startswith("5")]
    print(f"\nChecked {len(results)} links; {len(broken)} broken/suspicious.", file=sys.stderr)
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
