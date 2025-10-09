#!/usr/bin/env python3
"""Legacy metadata cleanup helpers for the skills catalog."""

from __future__ import annotations

import json
from pathlib import Path

from core.io_safe import write_json_atomic

SKILLS_PATH = Path("records/skills.json")
KNOWN_SKILLS_ROOT = Path("records/characters")


def scrub_skills_catalog(skills_path: Path) -> bool:
    """Remove deprecated fields from the canonical skills catalog."""
    if not skills_path.exists():
        raise FileNotFoundError(f"Skills catalog not found: {skills_path}")

    skills = json.loads(skills_path.read_text(encoding="utf-8"))
    removed = False

    for skill_data in skills.values():
        if "first_mentioned_in" in skill_data:
            skill_data.pop("first_mentioned_in", None)
            removed = True

    if removed:
        write_json_atomic(skills_path, skills, ensure_ascii=False, indent=2)
    return removed


def scrub_known_skills(root: Path) -> list[Path]:
    """Strip obsolete provenance hints from character known_skills files."""
    if not root.exists():
        return []

    updated_files: list[Path] = []

    for path in root.rglob("known_skills.json"):
        known = json.loads(path.read_text(encoding="utf-8"))
        changed = False

        for skill in known.values():
            first_learned = skill.get("first_learned")
            if isinstance(first_learned, dict) and "source_file" in first_learned:
                first_learned.pop("source_file", None)
                changed = True

        if changed:
            write_json_atomic(path, known, ensure_ascii=False, indent=2)
            updated_files.append(path)

    return updated_files


def main() -> None:
    """Entry point for the metadata cleanup script."""
    skills_updated = scrub_skills_catalog(SKILLS_PATH)
    if skills_updated:
        print("✅ Removed legacy first_mentioned_in blocks from skills.json")
    else:
        print("✅ No legacy first_mentioned_in fields found in skills.json")

    changed_files = scrub_known_skills(KNOWN_SKILLS_ROOT)
    if changed_files:
        print("✅ Cleaned redundant source_file entries from known_skills.json:")
        for file_path in changed_files:
            print(f"  - {file_path}")
    else:
        print("✅ No changes needed in known_skills.json files")


if __name__ == "__main__":
    main()
