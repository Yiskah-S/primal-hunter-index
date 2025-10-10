#!/usr/bin/env python3
"""Ensure tag usage aligns with the registry status."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from core.schema_utils import read_json

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = REPO_ROOT / "records"
TAG_REGISTRY_PATH = REPO_ROOT / "tagging" / "tag_registry.json"
SKIP_FILE_SUFFIXES = (".meta.json", ".review.json", ".provenance.json")


def _iter_record_files(records_root: Path) -> Iterator[Path]:
	for path in sorted(records_root.rglob("*.json")):
		if any(path.name.endswith(suffix) for suffix in SKIP_FILE_SUFFIXES):
			continue
		yield path


def _collect_tag_strings(data: Any) -> list[tuple[str, str]]:
	collected: list[tuple[str, str]] = []

	def _walk(node: Any, pointer: str = "") -> None:
		if isinstance(node, dict):
			for key, value in node.items():
				child_pointer = f"{pointer}.{key}" if pointer else key
				if key == "tags" and isinstance(value, list):
					for idx, item in enumerate(value):
						collected.append((f"{child_pointer}[{idx}]", item))
				else:
					_walk(value, child_pointer)
		elif isinstance(node, list):
			for idx, item in enumerate(node):
				child_pointer = f"{pointer}[{idx}]" if pointer else f"[{idx}]"
				_walk(item, child_pointer)

	_walk(data)
	return collected


def _load_registry(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
	by_id: dict[str, dict[str, Any]] = {}
	by_slug: dict[str, dict[str, Any]] = {}
	raw = read_json(path)
	if not isinstance(raw, dict):
		return by_id, by_slug

	for entries in raw.values():
		if not isinstance(entries, list):
			continue
		for entry in entries:
			if not isinstance(entry, dict):
				continue
			tag_id = entry.get("tag_id")
			slug = entry.get("tag")
			if isinstance(tag_id, str):
				by_id[tag_id] = entry
			if isinstance(slug, str):
				by_slug[slug] = entry
	return by_id, by_slug


def validate_tags(
	records_root: Path,
	registry_path: Path,
	mode: str = "draft",
) -> tuple[list[str], list[str]]:
	errors: list[str] = []
	warnings: list[str] = []

	by_id, by_slug = _load_registry(registry_path)
	if not by_id and not by_slug:
		errors.append(f"{registry_path}: tag registry is empty or invalid.")
		return errors, warnings

	for record_file in _iter_record_files(records_root):
		data = read_json(record_file)
		if data is None:
			continue
		collected = _collect_tag_strings(data)
		for pointer, raw_value in collected:
			if not isinstance(raw_value, str):
				errors.append(f"{record_file}: {pointer} contains non-string tag value {raw_value!r}")
				continue
			tag_value = raw_value.strip()
			if not tag_value:
				errors.append(f"{record_file}: {pointer} contains empty tag string")
				continue

			reg_entry: dict[str, Any] | None = None
			if tag_value in by_id:
				reg_entry = by_id[tag_value]
			elif tag_value in by_slug:
				reg_entry = by_slug[tag_value]
			elif tag_value.startswith("tag.") and tag_value.split(".")[-1] in by_slug:
				reg_entry = by_slug[tag_value.split(".")[-1]]

			if reg_entry is None:
				errors.append(f"{record_file}: {pointer} references unknown tag '{tag_value}'")
				continue

			status = reg_entry.get("status")
			if status == "candidate":
				message = (
					f"{record_file}: {pointer} references candidate tag '{reg_entry.get('tag_id', tag_value)}'"
				)
				if mode == "export":
					errors.append(message)
				else:
					warnings.append(message)

	return errors, warnings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Validate tag usage against the registry.")
	parser.add_argument(
		"--records-root",
		type=Path,
		default=RECORDS_ROOT,
		help="Root directory containing records data (default: %(default)s)",
	)
	parser.add_argument(
		"--registry",
		type=Path,
		default=TAG_REGISTRY_PATH,
		help="Path to tag_registry.json (default: %(default)s)",
	)
	parser.add_argument(
		"--mode",
		choices=["draft", "export"],
		default="draft",
		help="Draft mode downgrades candidate tags to warnings; export mode fails on them.",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	errors, warnings = validate_tags(args.records_root, args.registry, mode=args.mode)
	for warning in warnings:
		print(f"⚠️  {warning}")
	for error in errors:
		print(f"❌ {error}")
	return 1 if errors else 0


if __name__ == "__main__":
	raise SystemExit(main())
