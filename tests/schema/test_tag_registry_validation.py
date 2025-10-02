import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.validate_all_metadata import _validate_tag_usage


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent="\t"))


def test_validate_tag_usage_pass(tmp_path: Path):
    records = tmp_path / "records"
    registry = {
        "tag_classes": {"topic": {"description": ""}},
        "tags": {
            "stealth": {"class": "topic", "description": ""}
        }
    }
    write_json(records / "tag_registry.json", registry)
    write_json(records / "skills.json", {
        "Shadow Step": {
            "tags": ["stealth"]
        }
    })

    assert _validate_tag_usage(records, registry) == []


def test_validate_tag_usage_unknown_tag(tmp_path: Path):
    records = tmp_path / "records"
    registry = {
        "tag_classes": {"topic": {"description": ""}},
        "tags": {
            "stealth": {"class": "topic", "description": ""}
        }
    }
    write_json(records / "tag_registry.json", registry)
    write_json(records / "scene_index" / "example.json", {
        "tags": ["unknown_tag"]
    })

    errors = _validate_tag_usage(records, registry)
    assert errors
    assert "unknown_tag" in errors[0]
