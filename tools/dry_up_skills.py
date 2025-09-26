import json
from pathlib import Path

# === Config ===
skills_path = Path("canon/skills.json")
scene_index_root = Path("canon/scene_index")
known_skills_root = Path("canon/characters")

# === Load all scene_index files into lookup by scene_id
scene_lookup = {}
for path in scene_index_root.rglob("*.json"):
	if path.name == "__init__.py":
		continue
	with path.open() as f:
		data = json.load(f)
		scene_id = data.get("scene_id")
		if scene_id:
			scene_lookup[scene_id] = data.get("source_file")

# === Load and clean skills.json
with skills_path.open() as f:
	skills = json.load(f)

for skill_data in skills.values():
	first = skill_data.get("first_mentioned_in", {})
	scene_id = first.get("scene_id")
	if scene_id and "source_file" in first:
		indexed_file = scene_lookup.get(scene_id)
		if indexed_file and indexed_file == first["source_file"]:
			del first["source_file"]

# === Write back skills.json
with skills_path.open("w") as f:
	json.dump(skills, f, indent=2)
print("✅ Cleaned redundant source_file from skills.json")

# === Clean known_skills.json files
changed_files = []
for path in known_skills_root.rglob("known_skills.json"):
	with path.open() as f:
		known = json.load(f)

	changed = False
	for skill in known.values():
		first = skill.get("first_learned", {})
		if "source_file" in first:
			del first["source_file"]
			changed = True

	if changed:
		with path.open("w") as f:
			json.dump(known, f, indent=2)
		changed_files.append(str(path))

if changed_files:
	print("✅ Cleaned redundant source_file from known_skills.json:")
	for file in changed_files:
		print(f"  - {file}")
else:
	print("✅ No changes needed in known_skills.json files")
