#!/usr/bin/env python3
"""Show structural differences between the working schema and a Git ref."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from difflib import unified_diff


def _read_local_schema(schema_dir: Path, schema_name: str) -> Any:
    schema_path = schema_dir / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _read_schema_from_git(schema_path: Path, git_ref: str) -> Any:
    git_target = f"{git_ref}:{schema_path.as_posix()}"
    result = subprocess.run(
        ["git", "show", git_target],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to read {git_target}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _canonical_json(data: Any) -> list[str]:
    return json.dumps(data, indent=2, sort_keys=True).splitlines(keepends=True)


def _summarise_changes(current: Any, previous: Any) -> list[str]:
    summary: list[str] = []
    if isinstance(current, dict) and isinstance(previous, dict):
        current_keys = set(current.keys())
        previous_keys = set(previous.keys())
        added = sorted(current_keys - previous_keys)
        removed = sorted(previous_keys - current_keys)
        if added:
            summary.append(f"+ Added top-level keys: {', '.join(added)}")
        if removed:
            summary.append(f"- Removed top-level keys: {', '.join(removed)}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff a schema against a Git reference.")
    parser.add_argument("schema_dir", type=Path, help="Directory containing the schema (e.g., schemas/)")
    parser.add_argument("schema_name", help="Schema filename (e.g., skills.schema.json)")
    parser.add_argument(
        "git_ref",
        nargs="?",
        default="HEAD~1",
        help="Git reference to compare against (default: HEAD~1)",
    )
    args = parser.parse_args()

    try:
        current_schema = _read_local_schema(args.schema_dir, args.schema_name)
        previous_schema = _read_schema_from_git(args.schema_dir / args.schema_name, args.git_ref)
    except Exception as exc:  # pragma: no cover - surfaced to CLI
        print(f"Error: {exc}")
        return 1

    if current_schema == previous_schema:
        print("No structural differences detected.")
        return 0

    summary_lines = _summarise_changes(current_schema, previous_schema)
    if summary_lines:
        for line in summary_lines:
            print(line)
        print()

    diff_lines = unified_diff(
        _canonical_json(previous_schema),
        _canonical_json(current_schema),
        fromfile=f"{args.git_ref}:{args.schema_name}",
        tofile=f"workspace:{args.schema_name}",
    )
    sys.stdout.writelines(diff_lines)
    return 0


if __name__ == "__main__":
    sys.exit(main())
