import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))


def _validator_for(schema_path: Path) -> Draft202012Validator:
	schema = json.loads(schema_path.read_text())
	return Draft202012Validator(schema, resolver=RefResolver.from_schema(schema))


def test_record_log_fragment_validates_required_fields():
	schema_path = Path("schemas/shared/record_log.schema.json")
	schema = json.loads(schema_path.read_text())
	validator = Draft202012Validator(schema["$defs"]["record_log_entry"], resolver=RefResolver.from_schema(schema))

	valid_entry = {
		"entry_keys": ["skills.sf.meditation"],
		"added_by": "assistant",
		"date": "2025-10-08",
		"method": "manual_seed",
	}
	validator.validate(valid_entry)

	invalid_entry = {"entry_keys": ["skills.sf.meditation"], "added_by": "assistant", "date": "2025-10-08"}
	errors = list(validator.iter_errors(invalid_entry))
	assert errors
	assert any("method" in error.message for error in errors)


def test_timeline_event_schema_enforces_enum_values():
	schema_path = Path("schemas/timeline_event.schema.json")
	schema = json.loads(schema_path.read_text())
	store = {
		"https://primal-hunter.local/schemas/shared/provenance.schema.json": json.loads(
			Path("schemas/shared/provenance.schema.json").read_text()
		),
		"https://primal-hunter.local/schemas/shared/source_ref.schema.json": json.loads(
			Path("schemas/shared/source_ref.schema.json").read_text()
		),
		"https://primal-hunter.local/schemas/shared/id.schema.json": json.loads(
			Path("schemas/shared/id.schema.json").read_text()
		),
		"https://primal-hunter.local/schemas/shared/tags.schema.json": json.loads(
			Path("schemas/shared/tags.schema.json").read_text()
		),
	}
	validator = Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store=store))

valid_event = {
	"event_id": "ev.test_char.01.02.01.acquire_skill",
	"scene_id": "01.02.01",
	"order": 1,
	"type": "skill_acquired",
	"node_id": "sn.meditation.rank1",
	"knowledge_delta": [
		{"field_path": "rarity", "new_value": "Inferior", "confidence": 1.0},
	],
	"tags": ["tag.timeline.system_message"],
	"source_ref": [{"type": "scene", "scene_id": "01.02.01", "line_start": 12, "line_end": 14}],
}
	validator.validate(valid_event)

	invalid_event = {**valid_event, "type": "unknown_event"}
	errors = list(validator.iter_errors(invalid_event))
	assert errors
	assert any(error.message.startswith("'unknown_event' is not one of") for error in errors)
