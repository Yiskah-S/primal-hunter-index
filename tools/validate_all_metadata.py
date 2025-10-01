# Run command: python scripts/validate_all_metadata.py
# tools/
#├── validate_all_metadata.py  ← this should:
 #    - load all schema files from /schemas
#   - validate all data files in /records
   #  - call check_known_skills_consistency.py internally

# tools/validate_all_metadata.py

#!/usr/bin/env python3
"""Validate record metadata and enforce basic referential integrity."""

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from jsonschema import Draft202012Validator

from core.schema_utils import read_json

SCHEMA_ROOT = Path("schemas")
RECORDS_ROOT = Path("records")
CHARACTER_DIRECTORY = RECORDS_ROOT / "characters"

FILE_TO_SCHEMA_PATHS = {
	RECORDS_ROOT / "skills.json": SCHEMA_ROOT / "skills.schema.json",
	RECORDS_ROOT / "equipment.json": SCHEMA_ROOT / "equipment.schema.json",
	RECORDS_ROOT / "races.json": SCHEMA_ROOT / "races.schema.json",
	RECORDS_ROOT / "system_glossary.json": SCHEMA_ROOT / "system_glossary.schema.json",
	RECORDS_ROOT / "zone_lore.json": SCHEMA_ROOT / "zone_lore.schema.json",
	RECORDS_ROOT / "stat_scaling.json": SCHEMA_ROOT / "stat_scaling.schema.json",
	RECORDS_ROOT / "global_event_timeline.json": SCHEMA_ROOT / "global_event_timeline.schema.json",
	RECORDS_ROOT / "global_announcement_log.json": SCHEMA_ROOT / "global_announcement_log.schema.json",
	RECORDS_ROOT / "chapters_to_posts.json": SCHEMA_ROOT / "chapters_to_posts.schema.json",
	RECORDS_ROOT / "aliases" / "character_aliases.json": SCHEMA_ROOT / "aliases.schema.json",
	RECORDS_ROOT / "aliases" / "entity_aliases.json": SCHEMA_ROOT / "aliases.schema.json",
	RECORDS_ROOT / "tag_registry.json": SCHEMA_ROOT / "tag_registry.schema.json"
}

TIMELINE_SCHEMA = SCHEMA_ROOT / "character_timeline.schema.json"
SCENE_SCHEMA = SCHEMA_ROOT / "scene_index.schema.json"
META_SCHEMA = SCHEMA_ROOT / "file_metadata.schema.json"


class ValidationError(Exception):
	pass


TAG_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")


def _collect_schema_errors(data_path: Path, schema_path: Path) -> list[str]:
	schema_definition = read_json(schema_path)
	validator = Draft202012Validator(schema_definition)
	instance_data = read_json(data_path)
	error_messages: List[str] = []
	for validation_error in validator.iter_errors(instance_data):
		data_location = " → ".join(str(part) for part in validation_error.path) or "<root>"
		error_messages.append(f"{data_path}: {data_location}: {validation_error.message}")
	return error_messages


def _iter_scene_files() -> Iterable[Path]:
	scene_directory = RECORDS_ROOT / "scene_index"
	for scene_file in scene_directory.rglob("*.json"):
		if scene_file.name.endswith(".meta.json"):
			continue
		if scene_file.name == "__init__.py":
			continue
		yield scene_file


def _iter_meta_files() -> Iterable[Path]:
	return RECORDS_ROOT.rglob("*.meta.json")


def _iter_timeline_files() -> Iterable[Path]:
	if not CHARACTER_DIRECTORY.exists():
		return []
	for character_folder in CHARACTER_DIRECTORY.iterdir():
		if not character_folder.is_dir():
			continue
		timeline_path = character_folder / "timeline.json"
		if timeline_path.exists():
			yield timeline_path


def _validate_tag_usage(records_root: Path, tag_registry: dict) -> list[str]:
	errors: list[str] = []
	tag_definitions = tag_registry.get("tags") if isinstance(tag_registry, dict) else None
	if not tag_definitions:
		errors.append("records/tag_registry.json is missing 'tags' definitions.")
		return errors

	canonical_tags = set(tag_definitions.keys())
	alias_to_canonical: dict[str, str] = {}
	allow_inferred_map: dict[str, bool] = {}

	for tag_name, metadata in tag_definitions.items():
		if not isinstance(metadata, dict):
			errors.append(f"records/tag_registry.json → tag '{tag_name}' must map to an object definition.")
			continue
		allow_inferred_map[tag_name] = bool(metadata.get("allow_inferred"))
		aliases = metadata.get("aliases", [])
		if isinstance(aliases, list):
			for alias in aliases:
				if isinstance(alias, str):
					alias_to_canonical[alias] = tag_name
				else:
					errors.append(f"records/tag_registry.json → aliases for '{tag_name}' must be strings.")
		elif aliases is not None:
			errors.append(f"records/tag_registry.json → aliases for '{tag_name}' must be a list if provided.")

	def validate_tag_list(raw_value, pointer: str, file_path: Path) -> list[str]:
		issues: list[str] = []
		if not isinstance(raw_value, list):
			issues.append(f"{file_path}: {pointer} → tags must be a list.")
			return issues
		for index, entry in enumerate(raw_value):
			element_pointer = f"{pointer}/{index}"
			if isinstance(entry, str):
				tag_name = entry
				inferred = False
			elif isinstance(entry, dict):
				tag_name = entry.get("tag")
				if tag_name is None:
					issues.append(f"{file_path}: {element_pointer} → tag object missing 'tag' property.")
					continue
				if not isinstance(tag_name, str):
					issues.append(f"{file_path}: {element_pointer} → tag id must be a string.")
					continue
				inferred = entry.get("inferred", False)
				if not isinstance(inferred, bool):
					issues.append(f"{file_path}: {element_pointer} → 'inferred' must be a boolean if provided.")
				extra_keys = {k for k in entry.keys() if k not in {"tag", "inferred"}}
				if extra_keys:
					issues.append(f"{file_path}: {element_pointer} → unexpected keys {sorted(extra_keys)} in tag object.")
			else:
				issues.append(f"{file_path}: {element_pointer} → tag entries must be strings or objects with 'tag'.")
				continue

			if not TAG_NAME_PATTERN.fullmatch(tag_name):
				issues.append(f"{file_path}: {element_pointer} → tag '{tag_name}' must be lowercase snake_case.")
				continue

			canonical = tag_name
			if tag_name in alias_to_canonical:
				canonical = alias_to_canonical[tag_name]
				issues.append(
					f"{file_path}: {element_pointer} → tag '{tag_name}' is an alias; replace with canonical id '{canonical}'."
				)

			if canonical not in canonical_tags:
				issues.append(f"{file_path}: {element_pointer} → tag '{tag_name}' missing from records/tag_registry.json.")
				continue

			if inferred and not allow_inferred_map.get(canonical, False):
				issues.append(
					f"{file_path}: {element_pointer} → tag '{canonical}' cannot be marked inferred (allow_inferred is false)."
				)
		return issues

	def walk(node, pointer: str, *, file_path: Path):
		if isinstance(node, dict):
			for key, value in node.items():
				child_pointer = f"{pointer}/{key}" if pointer else key
				if key == "tags":
					errors.extend(validate_tag_list(value, child_pointer, file_path))
				else:
					walk(value, child_pointer, file_path=file_path)
		elif isinstance(node, list):
			for index, item in enumerate(node):
				child_pointer = f"{pointer}/{index}" if pointer else str(index)
				walk(item, child_pointer, file_path=file_path)

	for json_path in records_root.rglob("*.json"):
		if json_path.name.endswith(".meta.json"):
			continue
		if json_path.name == "tag_registry.json":
			continue
		data = read_json(json_path)
		walk(data, "", file_path=json_path)

	return errors


def validate_all() -> int:
	validation_errors: List[str] = []

	# Records files with direct schema mappings (skills, equipment, etc.)
	for data_path, schema_path in FILE_TO_SCHEMA_PATHS.items():
		if data_path.exists():
			validation_errors.extend(_collect_schema_errors(data_path, schema_path))

	# Scene index entries
	for scene_path in _iter_scene_files():
		validation_errors.extend(_collect_schema_errors(scene_path, SCENE_SCHEMA))

	# Character timelines and the skills they reference
	skill_catalog_names = set(read_json(RECORDS_ROOT / "skills.json").keys())
	skill_names_without_rarity = {
		full_name.split(" (")[0].strip(): full_name for full_name in skill_catalog_names
	}
	for timeline_path in _iter_timeline_files():
		validation_errors.extend(_collect_schema_errors(timeline_path, TIMELINE_SCHEMA))
		timeline_entries = read_json(timeline_path)
		for entry_index, timeline_entry in enumerate(timeline_entries):
			for timeline_skill in timeline_entry.get("skills", []):
				if timeline_skill in skill_catalog_names:
					continue
				skill_name_without_rarity = timeline_skill.split(" (")[0].strip()
				if skill_name_without_rarity not in skill_names_without_rarity:
					validation_errors.append(
						f"{timeline_path}: entry[{entry_index}].skills → '{timeline_skill}' missing from records/skills.json"
					)

	# Metadata sidecar files that store provenance
	for metadata_path in _iter_meta_files():
		validation_errors.extend(_collect_schema_errors(metadata_path, META_SCHEMA))

	# Tag usage across all record files
	tag_registry = read_json(RECORDS_ROOT / "tag_registry.json")
	validation_errors.extend(_validate_tag_usage(RECORDS_ROOT, tag_registry))

	if validation_errors:
		print("\n❌ Metadata validation failed:")
		for error_message in validation_errors:
			print(f" - {error_message}")
		return 1

	print("✅ All metadata files passed validation.")
	return 0


def main(argv: Optional[List[str]] = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.parse_args(argv)
	return validate_all()


if __name__ == "__main__":
	sys.exit(main())
