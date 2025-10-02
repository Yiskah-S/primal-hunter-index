import json
from pathlib import Path

skills_path = Path("records/skills.json")
known_skills_root = Path("records/characters")

# --- Remove legacy first_mentioned_in from skills catalog ---
with skills_path.open() as f:
    skills = json.load(f)

for skill_data in skills.values():
    skill_data.pop("first_mentioned_in", None)

with skills_path.open("w") as f:
    json.dump(skills, f, indent=2)

print("✅ Removed legacy first_mentioned_in blocks from skills.json")

# --- Clean known_skills.json files (still remove old source_file hints) ---
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
