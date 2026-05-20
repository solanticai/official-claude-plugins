#!/usr/bin/env python3
"""Offline keyword clusterer using TF-IDF + cosine similarity.

No API calls — runs without OAuth. Used by `keyword-research` skill as a
fallback when the Google Ads Keyword Ideas API isn't available.

Usage:
    python keyword_clusterer.py --input seeds.txt --output clusters.json --n-clusters 6
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "must", "can", "of", "to",
    "for", "with", "by", "from", "in", "on", "at", "this", "that",
    "these", "those", "me", "my", "your", "our", "their", "its",
}


def tokenise(text: str) -> List[str]:
    """Lowercase, split on non-alphanumeric, strip stop words."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def _tf(tokens: List[str]) -> Dict[str, float]:
    freq: Dict[str, int] = defaultdict(int)
    for t in tokens:
        freq[t] += 1
    total = len(tokens) or 1
    return {k: v / total for k, v in freq.items()}


def _idf(all_docs: List[List[str]]) -> Dict[str, float]:
    import math

    n = len(all_docs)
    df: Dict[str, int] = defaultdict(int)
    for doc in all_docs:
        seen = set(doc)
        for t in seen:
            df[t] += 1
    return {t: math.log((1 + n) / (1 + v)) + 1 for t, v in df.items()}


def _tfidf(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf = _tf(tokens)
    return {t: tf_val * idf.get(t, 0.0) for t, tf_val in tf.items()}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    import math

    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def cluster_keywords(
    keywords: List[str],
    n_clusters: int = 6,
) -> List[Dict[str, object]]:
    """Greedy nearest-neighbour clustering with TF-IDF similarity.

    Returns a list of cluster dicts, each with ``theme`` (top term) and
    ``keywords`` (list of strings).
    """
    if not keywords:
        return []
    tokenised = [tokenise(kw) for kw in keywords]
    idf = _idf(tokenised)
    vectors = [_tfidf(doc, idf) for doc in tokenised]

    # Seed clusters: pick the n_clusters keywords with the highest vector norm.
    import math

    norms = [
        (i, math.sqrt(sum(v * v for v in vec.values()))) for i, vec in enumerate(vectors)
    ]
    norms.sort(key=lambda x: -x[1])
    seed_indices = [i for i, _ in norms[:n_clusters]]

    clusters: List[Dict[str, object]] = []
    for idx in seed_indices:
        top_term = _top_term(vectors[idx])
        clusters.append(
            {
                "theme": top_term,
                "seed_index": idx,
                "keywords": [keywords[idx]],
                "centroid": dict(vectors[idx]),
            }
        )

    # Assign remaining keywords to the nearest cluster.
    for i, vec in enumerate(vectors):
        if i in seed_indices:
            continue
        best_cluster = max(
            clusters,
            key=lambda c: _cosine(vec, c["centroid"]),  # type: ignore[arg-type]
        )
        best_cluster["keywords"].append(keywords[i])  # type: ignore[list-item]
        # Update centroid (simple running average)
        centroid = best_cluster["centroid"]  # type: ignore[assignment]
        for k, v in vec.items():
            centroid[k] = (centroid.get(k, 0.0) + v) / 2  # type: ignore[call-overload]

    # Strip internal fields from output
    return [
        {"theme": c["theme"], "keywords": c["keywords"]}
        for c in clusters
    ]


def _top_term(vec: Dict[str, float]) -> str:
    if not vec:
        return "misc"
    return max(vec.items(), key=lambda kv: kv[1])[0]


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ppc-manager keyword clusterer")
    parser.add_argument("--input", type=Path, required=True, help="Text file with one keyword per line")
    parser.add_argument("--output", type=Path, default=None, help="JSON output path (default: stdout)")
    parser.add_argument("--n-clusters", type=int, default=6)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    keywords = [
        line.strip()
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    clusters = cluster_keywords(keywords, args.n_clusters)
    result = {"n_clusters": len(clusters), "clusters": clusters}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
