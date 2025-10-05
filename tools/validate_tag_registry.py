#!/usr/bin/env python3
"""Validate tag registry files against the schema and project guardrails."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import path
from typing import any

from core.schema_utils import read_json, validate_json_schema

REPO_ROOT = path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))

DEFAULT_REGISTRY_PATH = path("tagging/tag_registry.json")
DEFAULT_SCHEMA_PATH = path("schemas/tag_registry.schema.json")

ValidationResult = tuple[list[str], list[str]]  # (errors, warnings)


def _format_validation_errors(errors: Iterable[any], registry_path: path) -> list[str]:
	formatted: list[str] = []
	for error in errors:
		location = "/".join(str(part) for part in error.path) or "<root>"
		formatted.append(f"{registry_path}: {location}: {error.message}")
	return formatted


def _ensure_paths_exist(registry_path: path, schema_path: path) -> None:
	missing = [str(path) for path in (registry_path, schema_path) if not path.exists()]
	if missing:
		raise FileNotFoundError(f"Missing required file(s): {', '.join(missing)}")


def _validate_aliases(
	registry_path: path,
	pointer: str,
	tag_name: str,
	aliases: list[any],
	tag_occurrences: dict[str, str],
	alias_occurrences: dict[str, str],
) -> ValidationResult:
	errors: list[str] = []
	warnings: list[str] = []

	if aliases is None:
		aliases = []
	if not isinstance(aliases, list):
		errors.append(f"{registry_path}: {pointer}: aliases must be a list when provided")
		return errors, warnings

	for alias in aliases:
		if not isinstance(alias, str):
			errors.append(f"{registry_path}: {pointer}: alias entries must be strings")
			continue
		if alias == tag_name:
			warnings.append(f"{registry_path}: {pointer}: alias '{alias}' duplicates the canonical tag id")

		canonical_collision = tag_occurrences.get(alias)
		if canonical_collision and canonical_collision != pointer:
			errors.append(
				f"{registry_path}: {pointer}: alias '{alias}' collides with canonical tag "
				f"defined at {canonical_collision}"
			)
			continue

		alias_owner = alias_occurrences.get(alias)
		if alias_owner and alias_owner != tag_name:
			errors.append(
				f"{registry_path}: {pointer}: alias '{alias}' already assigned to tag '{alias_owner}'"
			)
			continue

		alias_occurrences[alias] = tag_name

	return errors, warnings


def _validate_tag_entry(
	registry_path: path,
	class_name: str,
	index: int,
	entry: any,
	tag_occurrences: dict[str, str],
	alias_occurrences: dict[str, str],
) -> ValidationResult:
	errors: list[str] = []
	warnings: list[str] = []
	pointer = f"{class_name}[{index}]"

	if not isinstance(entry, dict):
		errors.append(f"{registry_path}: {pointer}: entry must be an object")
		return errors, warnings

	tag_name = entry.get("tag")
	if not isinstance(tag_name, str):
		errors.append(f"{registry_path}: {pointer}: missing 'tag' string")
		return errors, warnings

	previous_definition = tag_occurrences.get(tag_name)
	if previous_definition is not None:
		errors.append(
			f"{registry_path}: {pointer}: duplicate tag id '{tag_name}' also defined at {previous_definition}"
		)
	else:
		tag_occurrences[tag_name] = pointer

	allow_inferred = entry.get("allow_inferred")
	status = entry.get("status")
	if isinstance(allow_inferred, bool) and allow_inferred and status != "approved":
		warnings.append(
			f"{registry_path}: {pointer}: allow_inferred=true on non-approved tag '{tag_name}'"
		)

	alias_errors, alias_warnings = _validate_aliases(
		registry_path,
		pointer,
		tag_name,
		entry.get("aliases", []),
		tag_occurrences,
		alias_occurrences,
	)
	errors.extend(alias_errors)
	warnings.extend(alias_warnings)

	return errors, warnings


def _validate_registry_content(registry_path: path, registry_payload: dict[str, any]) -> ValidationResult:
	errors: list[str] = []
	warnings: list[str] = []

	if not isinstance(registry_payload, dict):
		errors.append(f"{registry_path}: <root>: registry must be a JSON object")
		return errors, warnings

	tag_occurrences: dict[str, str] = {}
	alias_occurrences: dict[str, str] = {}

	for class_name, entries in registry_payload.items():
		if not isinstance(entries, list):
			errors.append(f"{registry_path}: {class_name}: expected an array of tag definitions")
			continue

		for index, entry in enumerate(entries):
			entry_errors, entry_warnings = _validate_tag_entry(
				registry_path,
				class_name,
				index,
				entry,
				tag_occurrences,
				alias_occurrences,
			)
			errors.extend(entry_errors)
			warnings.extend(entry_warnings)

	if not tag_occurrences:
		errors.append(f"{registry_path}: <root>: registry does not contain any tag entries")

	return errors, warnings


def validate_tag_registry(registry_path: path, schema_path: path) -> ValidationResult:
	_ensure_paths_exist(registry_path, schema_path)

	schema_errors = validate_json_schema(registry_path, schema_path)
	if schema_errors:
		return _format_validation_errors(schema_errors, registry_path), []

	payload = read_json(registry_path)
	return _validate_registry_content(registry_path, payload)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Validate the tag registry \
								against schema and guardrails")
	parser.add_argument(
		"--registry",
		type=path,
		default=DEFAULT_REGISTRY_PATH,
		help="path to the tag registry JSON file (default: tagging/tag_registry.json)",
	)
	parser.add_argument(
		"--schema",
		type=path,
		default=DEFAULT_SCHEMA_PATH,
		help="path to the tag registry schema \
			(default: schemas/tag_registry.schema.json)",
	)
	parser.add_argument(
		"--fail-on-warning",
		action="store_true",
		help="Exit with a non-zero status if warnings are encountered.",
	)
	return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
	args = parse_args(argv)
	registry_path = args.registry.resolve()
	schema_path = args.schema.resolve()

	try:
		errors, warnings = validate_tag_registry(registry_path, schema_path)
	except FileNotFoundError as exc:
		print(f"❌ {exc}")
		return 2

	if errors:
		print("❌ Tag registry validation failed:")
		for issue in errors:
			print(f"  - {issue}")
		if warnings:
			print("⚠️  Additional warnings:")
			for warning in warnings:
				print(f"  - {warning}")
		return 1

	if warnings:
		print("⚠️  Tag registry warnings:")
		for warning in warnings:
			print(f"  - {warning}")
		if args.fail_on_warning:
			return 1

	print(f"✅ Tag registry valid: {registry_path}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
