import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

SCHEMA_PATH = Path("schemas/character_timeline.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text())

_SHARED_STORE = {
	"https://primal-hunter.local/schemas/shared/resource_block.schema.json": json.loads(
		(SCHEMA_PATH.parent / "shared" / "resource_block.schema.json").read_text()
	),
	"https://primal-hunter.local/schemas/shared/provenance.schema.json": json.loads(
		(SCHEMA_PATH.parent / "shared" / "provenance.schema.json").read_text()
	),
	"https://primal-hunter.local/schemas/shared/source_ref.schema.json": json.loads(
		(SCHEMA_PATH.parent / "shared" / "source_ref.schema.json").read_text()
	),
}

RESOLVER = RefResolver.from_schema(SCHEMA, store=_SHARED_STORE)
VALIDATOR = Draft202012Validator(SCHEMA, resolver=RESOLVER)


def _collect_errors(instance_data):
    return list(VALIDATOR.iter_errors(instance_data))


def test_valid_timeline_entry_passes():
    minimal_timeline = [
        {
            "day": 1,
            "scene_id": "01-02-01",
            "stats": {
                "total": {"Str": 5},
                "sources": {
                    "base": {"Str": 5}
                }
            },
            "resources": {
                "HP": {"max": 90, "current": 90, "derived_from": "Vit"}
            },
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
    timeline_missing_stats = [
        {
            "day": 1,
            "scene_id": "01-02-01"
        }
    ]
    collected_errors = _collect_errors(timeline_missing_stats)
    assert collected_errors
    assert any(
        "stats" in "".join(str(path_part) for path_part in error.path)
        or error.message.startswith("'stats'")
        for error in collected_errors
    )
