#!/usr/bin/env python3
import json
from pathlib import Path
from core.schema_utils import read_json, write_json_atomic, load_schema, validate_instance

SKILLS_FILE = Path("canon/skills.json")
KNOWN_SCHEMA = Path("schemas/known_skills.schema.json")
CHAR_DIR = Path("canon/characters")
SCENE_DIR = Path("canon/scene_index")

def prompt(msg: str, default: str = "") -> str:
	val = input(f"{msg}{f' [{default}]' if default else ''}: ").strip()
	return val or default

def require(cond, msg: str):
	if not cond:
		raise SystemExit(f"❌ {msg}")

def main():
	character = prompt("Character (e.g., jake)").lower()
	require(character, "Character is required")

	skill = prompt("Skill name (exact match in skills.json)")
	require(skill, "Skill is required")

	skills = read_json(SKILLS_FILE)
	require(skill in skills, f"Skill '{skill}' not found in {SKILLS_FILE}")

	scene_id = prompt("Scene ID (e.g., 01-02-01)")
	scene_path = next(SCENE_DIR.rglob(f"*/{scene_id}.json"), None)
	require(scene_path and scene_path.exists(), f"Scene '{scene_id}' not found in {SCENE_DIR}")

	day = int(prompt("Day learned", "0"))
	source = prompt("Source (e.g., Level up, Title reward)")
	tags = [t.strip() for t in prompt("Tags (comma-sep, optional)", "").split(",") if t.strip()]
	notes = prompt("Notes (optional)", "")
	line = prompt("Line number (optional)", "")
	if line.isdigit():
		line = int(line)
	else:
		line = None

	entry = {
		"rarity": skills[skill]["rarity"],
		"first_learned": {
			"scene_id": scene_id,
			"day": day
		},
		"source": source
	}
	if line is not None:
		entry["first_learned"]["line"] = line
	if tags:
		entry["tags"] = tags
	if notes:
		entry["notes"] = notes

	# Load existing
	path = CHAR_DIR / character / "known_skills.json"
	known = read_json(path)
	known = known or {}

	# Insert or update
	known[skill] = entry

	# Validate against schema
	schema = load_schema(KNOWN_SCHEMA)
	validate_instance(known, schema)

	# Save
	write_json_atomic(path, known)
	print(f"✅ Assigned skill '{skill}' to {character} in {path}")

if __name__ == "__main__":
	main()
