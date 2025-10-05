import sys
from pathlib import Path

import pytest

from tools.validate_all_metadata import (
    _load_scene_bounds,
    _validate_canonical_record_file,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if PROJECT_ROOT.as_posix() not in sys.path:
    sys.path.append(PROJECT_ROOT.as_posix())


@pytest.fixture(scope="module")
def scene_bounds():
    bounds, errors = _load_scene_bounds()
    assert not errors, f"Scene index issues detected: {errors}"
    return bounds


def test_canon_entry_requires_source_ref(scene_bounds):
    data = {"Example": {"canon": True}}
    errors = _validate_canonical_record_file(Path("dummy.json"), data, scene_bounds)
    assert any("must include source_ref" in message for message in errors)


def test_source_ref_out_of_scene_range(scene_bounds):
    entry = {
        "Example": {
            "canon": True,
            "source_ref": {
                "scene_id": "01-01-01",
                "line_start": 999,
                "line_end": 1000,
            },
        }
    }
    errors = _validate_canonical_record_file(Path("dummy.json"), entry, scene_bounds)
    joined = "\n".join(errors)
    assert "fall outside" in joined
