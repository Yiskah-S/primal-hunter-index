#!/usr/bin/env python3
"""Validate event identifiers across timeline datasets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterator

from core.schema_utils import read_json

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = REPO_ROOT / "records"
EVENT_ID_PATTERN = re.compile(r"^ev\.[a-z0-9_]+\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[a-z0-9_]+$")


def _iter_timeline_files(records_root: Path) -> Iterator[Path]:
	char_dir = records_root / "characters"
	if char_dir.exists():
		for entry in sorted(char_dir.iterdir()):
			if not entry.is_dir():
				continue
			timeline_path = entry / "timeline.json"
			if timeline_path.exists():
				yield timeline_path

	global_timeline = records_root / "global_event_timeline.json"
	if global_timeline.exists():
		yield global_timeline


def _relative(path: Path, base: Path) -> str:
	try:
		return str(path.relative_to(base))
	except ValueError:
		return str(path)


def collect_event_id_findings(records_root: Path, *, strict: bool = False) -> tuple[list[str], list[str]]:
	errors: list[str] = []
	warnings: list[str] = []
	seen: dict[str, str] = {}

	for timeline_path in _iter_timeline_files(records_root):
		data = read_json(timeline_path)
		rel_path = _relative(timeline_path, REPO_ROOT)

		if not isinstance(data, list):
			errors.append(f"{rel_path}: expected timeline JSON array")
			continue

		for index, entry in enumerate(data):
			pointer = f"{rel_path}[{index}]"
			if not isinstance(entry, dict):
				errors.append(f"{pointer}: timeline entry must be an object")
				continue

			event_id = entry.get("event_id")
			if event_id is None:
				message = f"{pointer}: missing event_id"
				if strict:
					errors.append(message)
				else:
					warnings.append(message)
				continue
			if not isinstance(event_id, str):
				errors.append(f"{pointer}: event_id must be a string")
				continue
			if not EVENT_ID_PATTERN.fullmatch(event_id):
				errors.append(f"{pointer}: event_id '{event_id}' does not match {EVENT_ID_PATTERN.pattern}")
				continue
			if event_id in seen:
				errors.append(f"{pointer}: duplicate event_id also seen at {seen[event_id]}")
				continue
			seen[event_id] = pointer

	return errors, warnings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Validate timeline event identifiers.")
	parser.add_argument(
		"--records-root",
		type=Path,
		default=RECORDS_ROOT,
		help="Root directory containing records data (default: %(default)s)",
	)
	parser.add_argument(
		"--strict",
		action="store_true",
		help="Treat missing event_id values as errors instead of warnings.",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	errors, warnings = collect_event_id_findings(args.records_root, strict=args.strict)

	for warning in warnings:
		print(f"⚠️  {warning}")
	for error in errors:
		print(f"❌ {error}")

	if errors:
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())
