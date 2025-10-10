import json
from pathlib import Path

from tools.validate_tags import validate_tags


def write_json(path: Path, payload) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def make_registry(path: Path) -> None:
	registry = {
		"scene_type": [
			{
				"tag_id": "tag.scene_type.office_life",
				"tag": "office_life",
				"status": "approved",
			},
			{
				"tag_id": "tag.scene_type.system_event",
				"tag": "system_event",
				"status": "candidate",
			},
		]
	}
	write_json(path, registry)


def test_validate_tags_draft_warns_on_candidate(tmp_path: Path) -> None:
	records_root = tmp_path / "records"
	registry_path = tmp_path / "tagging" / "tag_registry.json"
	make_registry(registry_path)

	record = {
		"title": "Scene A",
		"tags": ["office_life", "system_event"],
	}
	write_json(records_root / "scene_index" / "scene.json", record)

	errors, warnings = validate_tags(records_root, registry_path, mode="draft")
	assert not errors
	assert warnings  # candidate usage downgraded to warning in draft


def test_validate_tags_export_fails_on_candidate(tmp_path: Path) -> None:
	records_root = tmp_path / "records"
	registry_path = tmp_path / "tagging" / "tag_registry.json"
	make_registry(registry_path)
	record = {"tags": ["system_event"]}
	write_json(records_root / "scene_index" / "scene.json", record)
	errors, warnings = validate_tags(records_root, registry_path, mode="export")
	assert errors  # candidate tag escalates to error
	assert not warnings


def test_validate_tags_unknown_tag_errors(tmp_path: Path) -> None:
	records_root = tmp_path / "records"
	registry_path = tmp_path / "tagging" / "tag_registry.json"
	make_registry(registry_path)
	record = {"tags": ["unknown_tag"]}
	write_json(records_root / "scene_index" / "scene.json", record)
	errors, warnings = validate_tags(records_root, registry_path, mode="draft")
	assert errors
	assert not warnings
