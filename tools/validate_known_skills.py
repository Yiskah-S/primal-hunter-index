#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(".")
SKILLS_FILE = ROOT / "canon/skills.json"
SCENES_DIR = ROOT / "canon/scene_index"
CHAR_DIR = ROOT / "canon/characters"

def read_json(p: Path):
	return json.loads(p.read_text()) if p.exists() else {}

def fail(msg: str):
	print(f"❌ {msg}")
	sys.exit(1)

def main():
	errors = 0
	skills = read_json(SKILLS_FILE)
	skill_names = set(skills.keys()) if isinstance(skills, dict) else set()

	for char_dir in sorted((CHAR_DIR.iterdir() if CHAR_DIR.exists() else [])):
		if not char_dir.is_dir():
			continue
		ledger_path = char_dir / "known_skills.json"
		if not ledger_path.exists():
			continue
		try:
			data = read_json(ledger_path)
			acqs = data.get("acquisitions", [])
			if not isinstance(acqs, list):
				print(f"❌ {ledger_path}: 'acquisitions' is not a list")
				errors += 1
				continue

			for i, e in enumerate(acqs):
				skill = e.get("skill")
				at = e.get("at", {})
				scene_id = at.get("scene_id")
				line = at.get("line", 0)

				if skill not in skill_names:
					print(f"❌ {ledger_path}#{i}: unknown skill '{skill}' (not in {SKILLS_FILE})")
					errors += 1
				if not (SCENES_DIR / f"{scene_id}.json").exists():
					print(f"❌ {ledger_path}#{i}: missing scene '{scene_id}' in {SCENES_DIR}")
					errors += 1
				if not isinstance(line, int):
					print(f"❌ {ledger_path}#{i}: non-integer line '{line}'")
					errors += 1
		except Exception as ex:
			print(f"❌ {ledger_path}: {ex}")
			errors += 1

	if errors:
		fail(f"{errors} validation error(s).")
	print("✅ known_skills validation OK")

if __name__ == "__main__":
	main()
