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
from collections.abc import Iterable
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

from core.schema_utils import read_json

SCHEMA_ROOT = Path("schemas")
RECORDS_ROOT = Path("records")
TAG_REGISTRY_PATH = Path("tagging") / "tag_registry.json"
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
    TAG_REGISTRY_PATH: SCHEMA_ROOT / "tag_registry.schema.json",
    RECORDS_ROOT / "skill_types.json": SCHEMA_ROOT / "skill_types.schema.json"
}

TIMELINE_SCHEMA = SCHEMA_ROOT / "character_timeline.schema.json"
SCENE_SCHEMA = SCHEMA_ROOT / "scene_index.schema.json"
META_SCHEMA = SCHEMA_ROOT / "file_metadata.schema.json"


class ValidationError(Exception):
    pass


TAG_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")

SceneBoundsMap = dict[str, tuple[int, int, Path]]
SourceRefEntry = tuple[str, dict[str, object]]

CANONICAL_RECORD_PATHS: tuple[Path, ...] = (
    RECORDS_ROOT / "skills.json",
    RECORDS_ROOT / "equipment.json",
    RECORDS_ROOT / "classes.json",
    RECORDS_ROOT / "races.json",
    RECORDS_ROOT / "system_glossary.json",
    RECORDS_ROOT / "zone_lore.json",
    RECORDS_ROOT / "stat_scaling.json",
    RECORDS_ROOT / "global_event_timeline.json",
    RECORDS_ROOT / "global_announcement_log.json",
    RECORDS_ROOT / "affiliations.json",
    RECORDS_ROOT / "creatures.json",
    RECORDS_ROOT / "titles.json",
    RECORDS_ROOT / "tiers.json",
    RECORDS_ROOT / "locations.json"
)

SHARED_SCHEMA_STORE = {
    "https://primal-hunter.local/schemas/shared/granted_by.schema.json": read_json(
        SCHEMA_ROOT / "shared" / "granted_by.schema.json"
    ),
    "https://primal-hunter.local/schemas/shared/flavor.schema.json": read_json(
        SCHEMA_ROOT / "shared" / "flavor.schema.json"
    ),
    "https://primal-hunter.local/schemas/shared/resource_block.schema.json": read_json(
        SCHEMA_ROOT / "shared" / "resource_block.schema.json"
    ),
    "https://primal-hunter.local/schemas/shared/tags.schema.json": read_json(
        SCHEMA_ROOT / "shared" / "tags.schema.json"
    ),
    "https://primal-hunter.local/schemas/shared/provenance.schema.json": read_json(
        SCHEMA_ROOT / "shared" / "provenance.schema.json"
    ),
    "https://primal-hunter.local/schemas/shared/source_ref.schema.json": read_json(
        SCHEMA_ROOT / "shared" / "source_ref.schema.json"
    ),
	"https://primal-hunter.local/schemas/shared/id.schema.json": read_json(
		SCHEMA_ROOT / "shared" / "id.schema.json"
	),
	"https://primal-hunter.local/schemas/shared/record_log.schema.json": read_json(
		SCHEMA_ROOT / "shared" / "record_log.schema.json"
	),
	"https://primal-hunter.local/schemas/timeline_event.schema.json": read_json(
		SCHEMA_ROOT / "timeline_event.schema.json"
	),
	"https://primal-hunter.local/schemas/skill_node.schema.json": read_json(
		SCHEMA_ROOT / "skill_node.schema.json"
	),
}


def _collect_schema_errors(data_path: Path, schema_path: Path) -> list[str]:
    schema_definition = read_json(schema_path)
    resolver = RefResolver.from_schema(schema_definition, store=SHARED_SCHEMA_STORE)
    validator = Draft202012Validator(schema_definition, resolver=resolver)
    instance_data = read_json(data_path)
    error_messages: list[str] = []
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


def _flatten_tag_registry(tag_registry: dict) -> dict[str, dict]:
    if not isinstance(tag_registry, dict):
        return {}
    if "tags" in tag_registry and isinstance(tag_registry["tags"], dict):
        return {
            name: metadata
            for name, metadata in tag_registry["tags"].items()
            if isinstance(metadata, dict)
        }

    flattened: dict[str, dict] = {}
    for class_name, entries in tag_registry.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            tag_name = entry.get("tag")
            if isinstance(tag_name, str):
                flattened[tag_name] = entry
    return flattened


def _validate_tag_usage(records_root: Path, tag_registry: dict) -> list[str]:  # noqa: C901
    errors: list[str] = []
    tag_definitions = _flatten_tag_registry(tag_registry)
    if not tag_definitions:
        errors.append(f"{TAG_REGISTRY_PATH}: does not contain any tag definitions.")
        return errors

    canonical_tags = set(tag_definitions.keys())
    alias_to_canonical: dict[str, str] = {}
    allow_inferred_map: dict[str, bool] = {}

    for tag_name, metadata in tag_definitions.items():
        if not isinstance(metadata, dict):
            errors.append(f"{TAG_REGISTRY_PATH}: tag '{tag_name}' must map to an object definition.")
            continue
        allow_inferred_map[tag_name] = bool(metadata.get("allow_inferred"))
        aliases = metadata.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                if isinstance(alias, str):
                    alias_to_canonical[alias] = tag_name
                else:
                    errors.append(f"{TAG_REGISTRY_PATH}: aliases for '{tag_name}' must be strings.")
        elif aliases is not None:
            errors.append(f"{TAG_REGISTRY_PATH}: aliases for '{tag_name}' must be a list if provided.")

    def validate_tag_list(raw_value, pointer: str, file_path: Path) -> list[str]:  # noqa: C901
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
                    issues.append(
                        f"{file_path}: {element_pointer} → unexpected keys "
                        f"{sorted(extra_keys)} in tag object."
                    )
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
                    f"{file_path}: {element_pointer} → tag '{tag_name}' is an alias; "
                    f"replace with canonical id '{canonical}'."
                )

            if canonical not in canonical_tags:
                issues.append(
                    f"{file_path}: {element_pointer} → tag '{tag_name}' missing from {TAG_REGISTRY_PATH}."
                )
                continue

            if inferred and not allow_inferred_map.get(canonical, False):
                issues.append(
                    f"{file_path}: {element_pointer} → tag '{canonical}' cannot be marked "
                    "inferred (allow_inferred is false)."
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


def _load_scene_bounds() -> tuple[SceneBoundsMap, list[str]]:
    scene_bounds: SceneBoundsMap = {}
    errors: list[str] = []
    for scene_path in _iter_scene_files():
        scene_data = read_json(scene_path)
        scene_id = scene_data.get("scene_id")
        start_line = scene_data.get("start_line")
        end_line = scene_data.get("end_line")
        if not scene_id:
            errors.append(f"{scene_path}: missing scene_id.")
            continue
        if not isinstance(start_line, int) or not isinstance(end_line, int):
            errors.append(
                f"{scene_path}: start_line/end_line must be integers to validate provenance ranges."
            )
            continue
        scene_bounds[scene_id] = (start_line, end_line, scene_path)
    return scene_bounds, errors


def _load_skill_types() -> set[str]:
    skill_types_path = RECORDS_ROOT / "skill_types.json"
    if not skill_types_path.exists():
        return set()
    registry = read_json(skill_types_path)
    types = registry.get("types", [])
    return {str(type_name) for type_name in types if isinstance(type_name, str)}


def _normalize_source_ref(
    source_ref: object,
    base_pointer: str,
    file_path: Path,
    errors: list[str],
) -> list[SourceRefEntry]:
    ranges: list[SourceRefEntry] = []
    ref_pointer = f"{base_pointer}/source_ref"
    if isinstance(source_ref, dict):
        ranges.append((ref_pointer, source_ref))
    elif isinstance(source_ref, list):
        if not source_ref:
            errors.append(f"{file_path}: {ref_pointer} → source_ref array must contain at least one range.")
        else:
            for index, entry in enumerate(source_ref):
                range_pointer = f"{ref_pointer}/{index}"
                if not isinstance(entry, dict):
                    errors.append(f"{file_path}: {range_pointer} → source_ref entries must be objects.")
                    continue
                ranges.append((range_pointer, entry))
    else:
        errors.append(f"{file_path}: {ref_pointer} → source_ref must be an object or array of objects.")
    return ranges


def _validate_source_ref_ranges(
    file_path: Path,
    base_pointer: str,
    source_ref: object,
    scene_bounds: SceneBoundsMap,
) -> list[str]:
    errors: list[str] = []
    for range_pointer, payload in _normalize_source_ref(source_ref, base_pointer, file_path, errors):
        if not isinstance(payload, dict):
            continue
        scene_id = payload.get("scene_id")
        line_start = payload.get("line_start")
        line_end = payload.get("line_end")
        if scene_id is None:
            errors.append(f"{file_path}: {range_pointer} → scene_id is required.")
            continue
        scene_info = scene_bounds.get(scene_id)
        if scene_info is None:
            errors.append(f"{file_path}: {range_pointer} → scene_id '{scene_id}' missing from scene index.")
            continue
        scene_start, scene_end, scene_path = scene_info
        if not isinstance(line_start, int) or not isinstance(line_end, int):
            errors.append(
                f"{file_path}: {range_pointer} → line_start and line_end must be integers."
            )
            continue
        if line_start < 1 or line_end < 1:
            errors.append(f"{file_path}: {range_pointer} → line_start/line_end must be positive.")
            continue
        if line_start > line_end:
            errors.append(
                f"{file_path}: {range_pointer} → line_start ({line_start}) cannot exceed line_end ({line_end})."
            )
            continue
        if line_start < scene_start or line_end > scene_end:
            errors.append(
                f"{file_path}: {range_pointer} → lines {line_start}-{line_end} fall "
                f"outside scene {scene_id} range {scene_start}-{scene_end} "
                f"({scene_path})."
            )
    return errors


def _validate_canonical_record_file(
    file_path: Path,
    data: object,
    scene_bounds: SceneBoundsMap,
) -> list[str]:
    errors: list[str] = []
    if isinstance(data, dict):
        entries = [(key, value) for key, value in data.items()]
    elif isinstance(data, list):
        entries = [(f"entry[{index}]", value) for index, value in enumerate(data)]
    else:
        return errors
    for pointer, entry in entries:
        if not isinstance(entry, dict):
            continue
        canon_value = entry.get("canon")
        if canon_value is None:
            errors.append(f"{file_path}: {pointer} → missing 'canon' flag (bool expected).")
            continue
        if not isinstance(canon_value, bool):
            errors.append(f"{file_path}: {pointer} → 'canon' must be a boolean value.")
            continue
        source_ref = entry.get("source_ref")
        if canon_value:
            if source_ref is None:
                errors.append(f"{file_path}: {pointer} → canon entries must include source_ref.")
                continue
            errors.extend(_validate_source_ref_ranges(file_path, pointer, source_ref, scene_bounds))
        elif source_ref is not None:
            errors.extend(_validate_source_ref_ranges(file_path, pointer, source_ref, scene_bounds))
    return errors


def _validate_timeline_provenance(
    timeline_path: Path,
    entries: object,
    scene_bounds: SceneBoundsMap,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(entries, list):
        return errors
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        pointer = f"entry[{index}]"
        source_ref = entry.get("source_ref")
        if source_ref is None:
            errors.append(f"{timeline_path}: {pointer} → timeline entries must include source_ref.")
            continue
        errors.extend(_validate_source_ref_ranges(timeline_path, pointer, source_ref, scene_bounds))
    return errors


def validate_all() -> int:  # noqa: C901
    validation_errors: list[str] = []
    skill_types_allowed = _load_skill_types()

    # Records files with direct schema mappings (skills, equipment, etc.)
    for data_path, schema_path in FILE_TO_SCHEMA_PATHS.items():
        if data_path.exists():
            validation_errors.extend(_collect_schema_errors(data_path, schema_path))

    # Scene index entries
    for scene_path in _iter_scene_files():
        validation_errors.extend(_collect_schema_errors(scene_path, SCENE_SCHEMA))

    scene_bounds, scene_bound_errors = _load_scene_bounds()
    validation_errors.extend(scene_bound_errors)

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
                        f"{timeline_path}: entry[{entry_index}].skills → '{timeline_skill}' "
                        "missing from records/skills.json"
                    )
        validation_errors.extend(
            _validate_timeline_provenance(timeline_path, timeline_entries, scene_bounds)
        )

    # Metadata sidecar files that store provenance
    for metadata_path in _iter_meta_files():
        validation_errors.extend(_collect_schema_errors(metadata_path, META_SCHEMA))

    # Tag usage across all record files
    tag_registry = read_json(TAG_REGISTRY_PATH)
    validation_errors.extend(_validate_tag_usage(RECORDS_ROOT, tag_registry))

    # Canonical record provenance checks
    for data_path in CANONICAL_RECORD_PATHS:
        if not data_path.exists():
            continue
        entry_data = read_json(data_path)
        validation_errors.extend(
            _validate_canonical_record_file(data_path, entry_data, scene_bounds)
        )
        if data_path == RECORDS_ROOT / "skills.json" and skill_types_allowed:
            if isinstance(entry_data, dict):
                for skill_name, payload in entry_data.items():
                    if not isinstance(payload, dict):
                        continue
                    skill_type = payload.get("type")
                    if isinstance(skill_type, str) and skill_type not in skill_types_allowed:
                        validation_errors.append(
                            f"{data_path}: {skill_name} → type '{skill_type}' missing from records/skill_types.json"
                        )

    if validation_errors:
        print("\n❌ Metadata validation failed:")
        for error_message in validation_errors:
            print(f" - {error_message}")
        return 1

    print("✅ All metadata files passed validation.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    return validate_all()


if __name__ == "__main__":
    sys.exit(main())
