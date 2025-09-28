# Run command: python scripts/validate_all_metadata.py
# tools/
#├── validate_all_metadata.py  ← this should:
 #    - load all schema files from /schemas
  #   - validate all data files in /canon
   #  - call check_known_skills_consistency.py internally

# tools/validate_all_metadata.py

#!/usr/bin/env python3
"""Validate canonical metadata and enforce basic referential integrity."""

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from jsonschema import Draft202012Validator

from core.schema_utils import read_json

SCHEMA_ROOT = Path("schemas")
CANON_ROOT = Path("canon")
CHARACTER_DIRECTORY = CANON_ROOT / "characters"

FILE_TO_SCHEMA_PATHS = {
	CANON_ROOT / "skills.json": SCHEMA_ROOT / "skills.schema.json",
	CANON_ROOT / "equipment.json": SCHEMA_ROOT / "equipment.schema.json",
	CANON_ROOT / "races.json": SCHEMA_ROOT / "races.schema.json",
	CANON_ROOT / "system_glossary.json": SCHEMA_ROOT / "system_glossary.schema.json",
	CANON_ROOT / "zone_lore.json": SCHEMA_ROOT / "zone_lore.schema.json",
	CANON_ROOT / "stat_scaling.json": SCHEMA_ROOT / "stat_scaling.schema.json",
	CANON_ROOT / "global_event_timeline.json": SCHEMA_ROOT / "global_event_timeline.schema.json",
	CANON_ROOT / "global_announcement_log.json": SCHEMA_ROOT / "global_announcement_log.schema.json",
	CANON_ROOT / "chapters_to_posts.json": SCHEMA_ROOT / "chapters_to_posts.schema.json",
	CANON_ROOT / "aliases" / "character_aliases.json": SCHEMA_ROOT / "aliases.schema.json",
	CANON_ROOT / "aliases" / "entity_aliases.json": SCHEMA_ROOT / "aliases.schema.json"
}

TIMELINE_SCHEMA = SCHEMA_ROOT / "character_timeline.schema.json"
SCENE_SCHEMA = SCHEMA_ROOT / "scene_index.schema.json"
META_SCHEMA = SCHEMA_ROOT / "file_metadata.schema.json"


class ValidationError(Exception):
	pass


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
	scene_directory = CANON_ROOT / "scene_index"
	for scene_file in scene_directory.rglob("*.json"):
		if scene_file.name.endswith(".meta.json"):
			continue
		if scene_file.name == "__init__.py":
			continue
		yield scene_file


def _iter_meta_files() -> Iterable[Path]:
	return CANON_ROOT.rglob("*.meta.json")


def _iter_timeline_files() -> Iterable[Path]:
	if not CHARACTER_DIRECTORY.exists():
		return []
	for character_folder in CHARACTER_DIRECTORY.iterdir():
		if not character_folder.is_dir():
			continue
		timeline_path = character_folder / "timeline.json"
		if timeline_path.exists():
			yield timeline_path


def validate_all() -> int:
	validation_errors: List[str] = []

	# Canon files with direct schema mappings (skills, equipment, etc.)
	for data_path, schema_path in FILE_TO_SCHEMA_PATHS.items():
		if data_path.exists():
			validation_errors.extend(_collect_schema_errors(data_path, schema_path))

	# Scene index entries
	for scene_path in _iter_scene_files():
		validation_errors.extend(_collect_schema_errors(scene_path, SCENE_SCHEMA))

	# Character timelines and the skills they reference
	skill_catalog_names = set(read_json(CANON_ROOT / "skills.json").keys())
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
						f"{timeline_path}: entry[{entry_index}].skills → '{timeline_skill}' missing from canon/skills.json"
					)

	# Metadata sidecar files that store provenance
	for metadata_path in _iter_meta_files():
		validation_errors.extend(_collect_schema_errors(metadata_path, META_SCHEMA))

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
