import json
from jsonschema import validate, ValidationError, Draft202012Validator
from pathlib import Path

# === File paths ===
schema_path = Path("schemas/known_skills.schema.json")
data_path = Path("canon/characters/jake/known_skills.json")

# === Load schema and data ===
with schema_path.open() as f:
	schema = json.load(f)

with data_path.open() as f:
	data = json.load(f)

# === Create validator (Draft 2020-12) ===
validator = Draft202012Validator(schema)

# === Validate ===
errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

if errors:
	print(f"❌ Validation failed with {len(errors)} error(s):")
	for err in errors:
		location = " → ".join(str(x) for x in err.absolute_path)
		print(f"  • {location}: {err.message}")
else:
	print("✅ Validation passed! File conforms to schema.")
