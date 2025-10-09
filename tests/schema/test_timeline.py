import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

SCHEMA_PATH = Path("schemas/character_timeline.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text())

_SHARED_STORE = {
	"https://primal-hunter.local/schemas/timeline_event.schema.json": json.loads(
		(SCHEMA_PATH.parent / "timeline_event.schema.json").read_text()
	),
	"https://primal-hunter.local/schemas/shared/provenance.schema.json": json.loads(
		(SCHEMA_PATH.parent / "shared" / "provenance.schema.json").read_text()
	),
	"https://primal-hunter.local/schemas/shared/source_ref.schema.json": json.loads(
		(SCHEMA_PATH.parent / "shared" / "source_ref.schema.json").read_text()
	),
	"https://primal-hunter.local/schemas/shared/id.schema.json": json.loads(
		(SCHEMA_PATH.parent / "shared" / "id.schema.json").read_text()
	),
}

RESOLVER = RefResolver.from_schema(SCHEMA, store=_SHARED_STORE)
VALIDATOR = Draft202012Validator(SCHEMA, resolver=RESOLVER)


def _collect_errors(instance_data):
    return list(VALIDATOR.iter_errors(instance_data))


def test_valid_timeline_entry_passes():
	minimal_timeline = [
		{
			"event_id": "ev.jake.01_02_01.acquire_meditation",
			"scene_id": "01-02-01",
			"order": 1,
			"type": "skill_acquired",
			"skill_id": "sn.meditation.rank1",
			"tags": ["tag.timeline.system_message"],
			"source_ref": [
				{
					"type": "scene",
					"scene_id": "01-02-01",
					"line_start": 100,
					"line_end": 120
				}
			]
		}
	]
	assert _collect_errors(minimal_timeline) == []


def test_missing_stats_fails():
	timeline_missing_fields = [
		{
			"event_id": "ev.jake.01_02_01.acquire_meditation",
			"scene_id": "01-02-01",
			"order": 1,
			"type": "skill_acquired"
		}
	]
	collected_errors = _collect_errors(timeline_missing_fields)
	assert collected_errors
	assert any(error.message.startswith("'source_ref'") for error in collected_errors)
