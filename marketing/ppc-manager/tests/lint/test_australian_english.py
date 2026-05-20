"""Fail if any SKILL.md uses US spelling for common words.

The check is lightweight — it only flags a small allowlist of high-frequency
US spellings that we reliably want to avoid. False positives are rare in
practice; if one occurs, update the allowlist or fix the source.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PLUGIN_ROOT / "skills"

# (bad pattern, preferred spelling). Patterns are case-insensitive whole-word.
BAD_SPELLINGS = [
    (r"\bcolor\b", "colour"),
    (r"\bcolors\b", "colours"),
    (r"\bcolored\b", "coloured"),
    (r"\borganize\b", "organise"),
    (r"\borganized\b", "organised"),
    (r"\borganizing\b", "organising"),
    (r"\borganization\b", "organisation"),
    (r"\boptimize\b", "optimise"),
    (r"\boptimized\b", "optimised"),
    (r"\boptimization\b", "optimisation"),
    (r"\bprioritize\b", "prioritise"),
    (r"\bprioritized\b", "prioritised"),
    (r"\brecognize\b", "recognise"),
    (r"\brecognized\b", "recognised"),
    (r"\bcustomize\b", "customise"),
    (r"\bcustomized\b", "customised"),
    (r"\bauthorize\b", "authorise"),
    (r"\bauthorized\b", "authorised"),
    (r"\bauthorization\b", "authorisation"),
    (r"\banalyze\b", "analyse"),
    (r"\banalyzed\b", "analysed"),
]

# Allow US spellings inside:
# - fenced code blocks (```...```)
# - URLs
# - OAuth scope strings (these are literal Google scope URIs)
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_URL_RE = re.compile(r"https?://\S+")


def _strip_allowed(text: str) -> str:
    text = _FENCE_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    return text


def _skill_md_files() -> List[Path]:
    return [p for p in SKILLS_DIR.glob("*/SKILL.md") if p.stat().st_size > 0]


@pytest.mark.parametrize("skill_path", _skill_md_files(), ids=lambda p: p.parent.name)
def test_no_us_spellings(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    cleaned = _strip_allowed(text)

    offences = []
    for pattern, preferred in BAD_SPELLINGS:
        for m in re.finditer(pattern, cleaned, flags=re.IGNORECASE):
            offences.append(f"{m.group(0)!r} -> {preferred!r}")

    assert not offences, (
        f"{skill_path.parent.name}: US spellings found:\n  " + "\n  ".join(offences)
    )
