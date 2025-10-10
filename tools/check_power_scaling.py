#!/usr/bin/env python3
"""Validate power scaling monotonicity across character timelines.

This lightweight check enforces the behavioral rules described in the
authoring workflow runbook:

* Levels (e.g., `level`, `class_level`, `race_level`) must not decrease
  unless the timeline event explicitly marks itself as a downgrade/reset.
* Tier/grade style fields must be monotonic (highest rank wins) unless
  a downgrade/reset marker is present.

The script focuses on obvious regressions so authors notice accidental
power drops. It is intentionally conservative—when unsure, it emits
warnings rather than guessing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CHAR_TIMELINES_ROOT = REPO_ROOT / "records" / "characters"

LEVEL_KEYS = {"level", "class_level", "race_level"}
TIER_RANK = {
	"i": 0,
	"h": 1,
	"g": 2,
	"f": 3,
	"e": 4,
	"d": 5,
	"c": 6,
	"b": 7,
	"a": 8,
	"s": 9,
	"ss": 10,
	"sss": 11,
	"x": 12,
	"xx": 13,
	"xxx": 14,
}
GRADE_RANK = {
	"inferior": 0,
	"common": 1,
	"uncommon": 2,
	"rare": 3,
	"epic": 4,
	"legendary": 5,
	"mythic": 6,
	"transcendent": 7,
	"other": 8,
}


def _iter_timeline_files(root: Path) -> list[Path]:
	if not root.exists():
		return []
	return sorted(path / "timeline.json" for path in root.iterdir() if path.is_dir() and (path / "timeline.json").exists())


def _load_timeline(path: Path) -> list[dict[str, Any]]:
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
	except FileNotFoundError:
		return []
	except json.JSONDecodeError as exc:
		raise ValueError(f"{path}: invalid JSON: {exc}") from exc
	if not isinstance(data, list):
		raise ValueError(f"{path}: timeline must be a JSON array")
	return [entry for entry in data if isinstance(entry, dict)]


def _downgrade_allowed(entry: dict[str, Any]) -> bool:
	if entry.get("downgrade_event") is True or entry.get("reset_event") is True:
		return True
	tags = entry.get("tags")
	if isinstance(tags, list):
		for tag in tags:
			if not isinstance(tag, str):
				continue
			if "downgrade" in tag.lower() or "reset" in tag.lower():
				return True
	return False


def _grade_index(value: Any, mapping: dict[str, int]) -> int | None:
	if not isinstance(value, str):
		return None
	return mapping.get(value.strip().lower())


def _check_timeline(path: Path) -> tuple[list[str], list[str]]:
	errors: list[str] = []
	warnings: list[str] = []

	prev_numeric: dict[str, int] = {}
	prev_grade: dict[str, int] = {}
	prev_tier: dict[str, int] = {}

	timeline = _load_timeline(path)
	for index, entry in enumerate(timeline):
		allow_drop = _downgrade_allowed(entry)

		for key in LEVEL_KEYS:
			value = entry.get(key)
			if isinstance(value, int):
				prev = prev_numeric.get(key)
				if prev is not None and value < prev and not allow_drop:
					errors.append(
						f"{path}: event[{index}] {key} decreased {prev} → {value} without downgrade/reset marker."
					)
				prev_numeric[key] = value
			elif allow_drop and key in prev_numeric:
				# reset baseline after explicit downgrade
				prev_numeric[key] = entry.get(key) if isinstance(entry.get(key), int) else prev_numeric[key]

		grade_value = _grade_index(entry.get("grade"), GRADE_RANK)
		if grade_value is not None:
			prev = prev_grade.get("grade")
			if prev is not None and grade_value < prev and not allow_drop:
				errors.append(
					f"{path}: event[{index}] grade regressed ({entry.get('grade')}) without downgrade/reset marker."
				)
			prev_grade["grade"] = grade_value

		tier_value = _grade_index(entry.get("tier"), TIER_RANK)
		if tier_value is not None:
			prev = prev_tier.get("tier")
			if prev is not None and tier_value < prev and not allow_drop:
				warnings.append(
					f"{path}: event[{index}] tier decreased ({entry.get('tier')}); review manually or add downgrade marker."
				)
			prev_tier["tier"] = tier_value

	return errors, warnings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Check power scaling monotonicity across character timelines.")
	parser.add_argument(
		"--characters-root",
		type=Path,
		default=CHAR_TIMELINES_ROOT,
		help="Root directory containing character folders (default: %(default)s)",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	errors: list[str] = []
	warnings: list[str] = []

	for timeline_path in _iter_timeline_files(args.characters_root):
		timeline_errors, timeline_warnings = _check_timeline(timeline_path)
		errors.extend(timeline_errors)
		warnings.extend(timeline_warnings)

	for warning in warnings:
		print(f"⚠️  {warning}")
	for error in errors:
		print(f"❌ {error}")
	return 1 if errors else 0


if __name__ == "__main__":
	raise SystemExit(main())
