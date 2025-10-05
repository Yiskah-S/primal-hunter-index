import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path("schemas/character_timeline.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


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
            }
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
