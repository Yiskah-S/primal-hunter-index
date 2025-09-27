#!/usr/bin/env python3
import json
from pathlib import Path
from core.schema_utils import read_json, write_json_atomic, load_schema, validate_instance

SKILLS_FILE = Path("canon/skills.json")
SCHEMA_FILE = Path("schemas/character_timeline.schema.json")
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
	scene_file = next(SCENE_DIR.rglob(f"*/{scene_id}.json"), None)
	require(scene_file and scene_file.exists(), f"Scene '{scene_id}' not found in {SCENE_DIR}")

	day = int(prompt("Day learned", "0"))
	source = prompt("Source (e.g., Level up, Title reward)", "")
	line = prompt("Line number (optional)", "")
	line = int(line) if line.isdigit() else None
	reason = prompt("Reason (optional summary of how skill was acquired)", f"Gained skill: {skill}")
	tags = [t.strip() for t in prompt("Tags (comma-sep, optional)", "").split(",") if t.strip()]

	# Load timeline
	timeline_path = CHAR_DIR / character / "timeline.json"
	timeline = read_json(timeline_path)
	if not isinstance(timeline, list):
		print("⚠️ Creating new timeline file.")
		timeline = []

	# Try to find existing entry for this day + scene
	existing = next((snap for snap in timeline if snap.get("day") == day and snap.get("scene_id") == scene_id), None)
	if not existing:
		existing = {
			"day": day,
			"scene_id": scene_id,
			"source_file": str(scene_file),
			"reason": reason,
			"stats": { "total": {} }  # Minimal placeholder to satisfy schema
		}
		timeline.append(existing)

	# Append skill
	existing.setdefault("skills", []).append(skill)

	# Log it
	skill_log_entry = {"skill": skill, "source": source}
	if line: skill_log_entry["line"] = line
	existing.setdefault("skill_log", []).append(skill_log_entry)

	# Optional tags
	if tags:
		existing.setdefault("tags", []).extend(tags)

	# Sort and validate
	timeline.sort(key=lambda x: (x.get("day", 0), x.get("scene_id", "")))
	schema = load_schema(SCHEMA_FILE)
	validate_instance(timeline, schema)
	write_json_atomic(timeline_path, timeline)

	print(f"✅ Skill '{skill}' assigned to {character} timeline snapshot on day {day} ({scene_id})")

if __name__ == "__main__":
	main()
