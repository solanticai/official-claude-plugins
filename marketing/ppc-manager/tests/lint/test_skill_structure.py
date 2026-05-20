"""Validate every SKILL.md matches the ppc-manager conventions.

- YAML frontmatter parses.
- Required fields present.
- ``description`` <= 250 chars.
- File <= 500 lines.
- Required headings present.
- 3-6 '### Phase N:' sections.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PLUGIN_ROOT / "skills"

FRONTMATTER_FIELDS_REQUIRED = {"name", "description", "argument-hint", "allowed-tools", "effort"}
FRONTMATTER_FIELDS_ALLOWED = FRONTMATTER_FIELDS_REQUIRED | {
    "context",
    "agent",
    "paths",
    "model",
    "ultrathink",
    "disable-model-invocation",
    "user-invocable",
    "hooks",
    "shell",
}
REQUIRED_HEADINGS = [
    "## Skill Metadata",
    "## Description",
    "## User Context",
    "## Behavioural Rules",
    "## Edge Cases",
]
EFFORT_VALUES = {"low", "medium", "high", "max"}
MAX_LINES = 500
MAX_DESCRIPTION_CHARS = 250


def _parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (frontmatter dict, body text). Raise ValueError on malformed frontmatter."""
    if not text.startswith("---\n"):
        raise ValueError("Missing frontmatter fence")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("Missing closing frontmatter fence")
    block = text[4:end]
    body = text[end + 5 :]
    fm: Dict[str, Any] = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Malformed frontmatter line: {line}")
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, body


def _skill_files() -> List[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _non_empty_skill_files() -> List[Path]:
    """Skill files with content (size > 0) — allows Phase 1 to ship without every skill filled in."""
    return [p for p in _skill_files() if p.stat().st_size > 0]


@pytest.mark.parametrize("skill_path", _non_empty_skill_files(), ids=lambda p: p.parent.name)
def test_skill_structure(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    assert text, f"{skill_path} is empty"

    fm, body = _parse_frontmatter(text)

    missing_required = FRONTMATTER_FIELDS_REQUIRED - set(fm.keys())
    assert not missing_required, (
        f"{skill_path.parent.name}: missing required frontmatter fields: {missing_required}"
    )

    unknown = set(fm.keys()) - FRONTMATTER_FIELDS_ALLOWED
    assert not unknown, (
        f"{skill_path.parent.name}: unknown frontmatter fields: {unknown}"
    )

    assert fm["name"] == skill_path.parent.name, (
        f"{skill_path}: frontmatter name '{fm['name']}' does not match directory name"
    )

    assert len(fm["description"]) <= MAX_DESCRIPTION_CHARS, (
        f"{skill_path.parent.name}: description is "
        f"{len(fm['description'])} chars (max {MAX_DESCRIPTION_CHARS})"
    )

    assert fm["effort"] in EFFORT_VALUES, (
        f"{skill_path.parent.name}: effort '{fm['effort']}' not in {EFFORT_VALUES}"
    )

    lines = text.splitlines()
    assert len(lines) <= MAX_LINES, (
        f"{skill_path.parent.name}: {len(lines)} lines (max {MAX_LINES})"
    )

    for heading in REQUIRED_HEADINGS:
        assert heading in body, (
            f"{skill_path.parent.name}: missing required heading '{heading}'"
        )

    phases = re.findall(r"^### Phase \d+", body, flags=re.MULTILINE)
    assert 3 <= len(phases) <= 7, (
        f"{skill_path.parent.name}: expected 3-7 phases, found {len(phases)}"
    )

    assert "$ARGUMENTS" in body, (
        f"{skill_path.parent.name}: missing $ARGUMENTS placeholder in ## User Context"
    )


def test_at_least_oauth_setup_exists():
    """Phase 1 requires oauth-setup specifically to be populated."""
    path = SKILLS_DIR / "oauth-setup" / "SKILL.md"
    assert path.exists(), "skills/oauth-setup/SKILL.md must exist"
    assert path.stat().st_size > 0, "skills/oauth-setup/SKILL.md must not be empty"
