# Run command: python scripts/validate_all_metadata.py

import json
import os
from jsonschema import validate, ValidationError

# Pairs of metadata files and their corresponding schemas
VALIDATION_TARGETS = [
	("metadata/skills.json", "schemas/skills.schema.json"),
	("metadata/classes.json", "schemas/classes.schema.json"),
	("metadata/titles.json", "schemas/titles.schema.json"),
	("metadata/tiers.json", "schemas/tiers.schema.json"),
	("character_timeline/jake.json", "schemas/character_timeline.schema.json"),
	# Add more as you build them
]

def load_json(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)

def validate_json(metadata_path, schema_path):
	try:
		data = load_json(metadata_path)
		schema = load_json(schema_path)
		validate(instance=data, schema=schema)
		print(f"✅ {metadata_path} is valid against {schema_path}")
	except ValidationError as e:
		print(f"❌ {metadata_path} failed validation")
		print(f"   → {e.message}")
	except Exception as e:
		print(f"⚠️ Error with {metadata_path} or {schema_path}: {e}")

if __name__ == "__main__":
	for meta_file, schema_file in VALIDATION_TARGETS:
		if os.path.exists(meta_file) and os.path.exists(schema_file):
			validate_json(meta_file, schema_file)
		else:
			print(f"⚠️ Skipped missing: {meta_file} or {schema_file}")
