# scripts/validate_metadata.py

import json
from jsonschema import validate, ValidationError

def load_json(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)

def validate_json(instance_path, schema_path):
	try:
		instance = load_json(instance_path)
		schema = load_json(schema_path)
		validate(instance=instance, schema=schema)
		print(f"✅ {instance_path} is valid against {schema_path}")
	except ValidationError as e:
		print(f"❌ Validation failed for {instance_path}")
		print(f"   → {e.message}")
	except Exception as e:
		print(f"⚠️ Error loading files: {e}")

if __name__ == "__main__":
	validate_json("canon/skills.json", "schemas/skills.schema.json")
