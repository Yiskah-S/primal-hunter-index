import json
from pathlib import Path

# === Paths ===
skills_path = Path("canon/skills.json")
known_path = Path("canon/characters/jake/known_skills.json")  # or loop all characters

# === Load ===
with skills_path.open() as f:
	skills = json.load(f)

with known_path.open() as f:
	known_skills = json.load(f)

# === Check ===
unknown = set(known_skills.keys()) - set(skills.keys())
mismatched = []

for skill_name, meta in known_skills.items():
	expected = skills.get(skill_name)
	if expected and meta["rarity"] != expected["rarity"]:
		mismatched.append((skill_name, meta["rarity"], expected["rarity"]))

# === Report ===
if unknown:
	print("❌ Unknown skills (not in skills.json):")
	for s in unknown:
		print(f"  - {s}")
else:
	print("✅ All skills in known_skills are defined in skills.json")

if mismatched:
	print("❌ Rarity mismatches:")
	for s, got, expected in mismatched:
		print(f"  - {s}: got {got}, expected {expected}")
else:
	print("✅ All skill rarities match.")
