#!/usr/bin/env python3
import json
from pathlib import Path

SKILLS_FILE = Path("canon/skills.json")
SCENES_DIR = Path("canon/scene_index")
CHAR_DIR = Path("canon/characters")

def read_json(path: Path):
	return json.loads(path.read_text()) if path.exists() else {}

def write_json_atomic(path: Path, data):
	tmp = path.with_suffix(path.suffix + ".tmp")
	tmp.write_text(json.dumps(data, indent=2))
	tmp.replace(path)

def prompt(msg: str, default: str = "") -> str:
	val = input(f"{msg}{f' [{default}]' if default else ''}: ").strip()
	return val or default

def require(cond: bool, msg: str):
	if not cond:
		raise SystemExit(f"Error: {msg}")

def main():
	character = prompt("Character (e.g., jake, arnold)").lower()
	require(character, "character is required")

	skill = prompt("Skill name (exact, as in skills.json)")
	require(skill, "skill is required")

	scene_id = prompt("Scene ID (e.g., 0002-1)")
	source_file = prompt("Source file", "0002_Chapter_2_Introduction.md")
	line = prompt("Line number", "0")
	method = prompt("Method of acquisition", "System Tutorial")
	rank = prompt("Rank at acquisition (optional, hit Enter to skip)", "")
	notes = prompt("Notes (optional)", "")
	tags = [t.strip() for t in prompt("Tags (comma-sep)", "").split(",") if t.strip()]

	# load catalogs
	skills = read_json(SKILLS_FILE)
	require(skill in skills or any(k == skill for k in (skills.keys() if isinstance(skills, dict) else [])),
		f"skill '{skill}' not found in {SKILLS_FILE}")

	require((SCENES_DIR / f"{scene_id}.json").exists(),
		f"scene id '{scene_id}' not found in {SCENES_DIR}/")

	# load character ledger
	char_path = CHAR_DIR / character
	ledger_path = char_path / "known_skills.json"
	char_path.mkdir(parents=True, exist_ok=True)
	ledger = read_json(ledger_path)
	if not ledger:
		ledger = {"acquisitions": []}
	require(isinstance(ledger.get("acquisitions", []), list), "malformed known_skills.json (missing 'acquisitions' list)")

	entry = {
		"skill": skill,
		"at": {
			"scene_id": scene_id,
			"source_file": source_file,
			"line": int(line or "0")
		},
		"method": method
	}
	if rank:
		entry["rank"] = rank
	if notes:
		entry["notes"] = notes
	if tags:
		entry["tags"] = tags

	# append & keep stable sort by scene_id then line
	acqs = ledger["acquisitions"]
	acqs.append(entry)
	acqs.sort(key=lambda e: (e.get("at", {}).get("scene_id", ""), e.get("at", {}).get("line", 0)))

	write_json_atomic(ledger_path, ledger)
	print(f"✅ Added acquisition for '{character}': {skill} @ {scene_id}")

if __name__ == "__main__":
	main()
