#!/usr/bin/env python3
import json
from pathlib import Path
from core.schema_utils import read_json, write_json_atomic, load_schema, validate_instance

SKILLS_FILE = "canon/skills.json"
SCHEMA_FILE = "schemas/skills.schema.json"

def prompt(msg: str, default: str = "") -> str:
	val = input(f"{msg}{f' [{default}]' if default else ''}: ").strip()
	return val or default

def main() -> None:
	schema = load_schema(SCHEMA_FILE)
	skills = read_json(SKILLS_FILE)

	name = prompt("Skill name (use exact rarity in name, e.g., Identify (Inferior))")
	if not name:
		print("Aborted: skill name required.")
		return
	if name in skills:
		print(f"Aborted: '{name}' already exists.")
		return

	record = {
		"rarity": prompt("Rarity", "Inferior"),
		"type": prompt("Type", "General Utility"),
		"description": prompt("Description"),
		"effects": {
			"proficiency_with": [],
			"stat_synergy": {},
			"passive_benefit": prompt("Passive benefit (optional)", "")
		},
		"first_mentioned_in": {
			"scene_id": prompt("Scene ID", "ch2-intro"),
			"source_file": prompt("Source file", "0002_Chapter_2_Introduction.md"),
			"line": int(prompt("Line number", "231") or "0"),
		},
		"flavor": prompt("Flavor text"),
		"behavior": {
			"activation_method": prompt("Activation method", "Focus on target"),
			"deactivation": prompt("Deactivation", "Auto after use"),
			"instinctive_knowledge": prompt("Instinctive knowledge? (y/n)", "y").lower().startswith("y"),
			"feedback": prompt("Feedback", "Popup with details")
		},
		"tags": [t.strip() for t in prompt("Tags (comma-sep)", "tutorial,identify,info").split(",") if t.strip()],
		"granted_by": prompt("Granted by", "System Tutorial")
	}

	# assemble final object keyed by skill name (your convention)
	instance = {name: record}

	# validate full object (so schema that expects mapping is honored)
	validate_instance(instance, schema)

	# merge and write
	skills.update(instance)
	Path(SKILLS_FILE).parent.mkdir(parents=True, exist_ok=True)
	write_json_atomic(SKILLS_FILE, skills)
	print(f"✅ Added '{name}' to {SKILLS_FILE}")

if __name__ == "__main__":
	main()
