#!/usr/bin/env python3
import sys
from pathlib import Path
from core.schema_utils import read_json, load_schema, validate_instance

def validate_timeline(timeline_path: Path, schema_path: Path) -> None:
	timeline = read_json(timeline_path)
	schema = load_schema(schema_path)
	try:
		validate_instance(timeline, schema)
		print(f"✅ {timeline_path} is valid against {schema_path}")
	except ValueError as e:
		print(f"❌ Validation failed for {timeline_path}")
		print(e)

if __name__ == "__main__":
	timeline_file = Path("canon/characters/jake/timeline.json")
	schema_file = Path("schemas/character_timeline.schema.json")

	if not timeline_file.exists():
		sys.exit(f"❌ File not found: {timeline_file}")
	if not schema_file.exists():
		sys.exit(f"❌ File not found: {schema_file}")

	validate_timeline(timeline_file, schema_file)
