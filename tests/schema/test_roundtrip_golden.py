import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if PROJECT_ROOT.as_posix() not in sys.path:
    sys.path.append(PROJECT_ROOT.as_posix())

from core.schema_utils import read_json

SKILLS_PATH = Path("records/skills.json")
SKILL_SCHEMA_PATH = Path("schemas/skills.schema.json")
PROVENANCE_SCHEMA_PATH = Path("schemas/shared/provenance.schema.json")
GRANTED_BY_SCHEMA_PATH = Path("schemas/shared/granted_by.schema.json")


def test_basic_archery_round_trip_and_validation():
    skills = read_json(SKILLS_PATH)
    assert "Basic Archery" in skills, "Basic Archery must stay present as the golden baseline."

    original_entry = copy.deepcopy(skills["Basic Archery"])

    encoded = json.dumps(original_entry, sort_keys=True)
    decoded_entry = json.loads(encoded)

    assert decoded_entry == original_entry, "Serialisation round-trip must preserve the Basic Archery definition."

    skill_schema = read_json(SKILL_SCHEMA_PATH)
    entry_schema = skill_schema["$defs"]["entry"]

    schema_store = {
        "https://primal-hunter.local/schemas/shared/provenance.schema.json": read_json(PROVENANCE_SCHEMA_PATH),
        "https://primal-hunter.local/schemas/shared/granted_by.schema.json": read_json(GRANTED_BY_SCHEMA_PATH),
    }

    resolver = RefResolver.from_schema(skill_schema, store=schema_store)
    validator = Draft202012Validator(entry_schema, resolver=resolver)

    errors = sorted(validator.iter_errors(decoded_entry), key=lambda e: e.path)
    assert not errors, "Basic Archery must validate against the entry schema: " + "; ".join(
        f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors
    )
