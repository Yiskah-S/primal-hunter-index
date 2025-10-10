#!/usr/bin/env python3
"""Fail if any file contains a hyphenated scene ID (BB-CC-SS).

Usage (pre-commit passes filenames automatically):
    python tools/check_scene_ids.py FILE [FILE...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCENE_PATTERN = re.compile(r"\b\d{2}-\d{2}-\d{2}\b")


def check_file(path: Path) -> list[str]:
	try:
		text = path.read_text(encoding="utf-8")
	except (OSError, UnicodeDecodeError):
		return []
	violations: list[str] = []
	for idx, line in enumerate(text.splitlines(), start=1):
		if SCENE_PATTERN.search(line):
			violations.append(f"{path}:{idx}: hyphenated scene ID found")
	return violations


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Detect hyphenated scene IDs in changed files.")
	parser.add_argument("files", nargs="*", help="Files to scan")
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	all_findings: list[str] = []
	for filename in args.files:
		findings = check_file(Path(filename))
		all_findings.extend(findings)

	for finding in all_findings:
		print(f"❌ {finding}")
	return 1 if all_findings else 0


if __name__ == "__main__":
	raise SystemExit(main())
