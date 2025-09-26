# Run command: python scripts/validate_all_metadata.py
# tools/
#├── validate_all_metadata.py  ← this should:
 #    - load all schema files from /schemas
  #   - validate all data files in /canon
   #  - call check_known_skills_consistency.py internally

# tools/validate_all_metadata.py

from core.schema_utils import validate_json_schema
from tools.check_known_skills_consistency import check_known_skills_vs_skills
from pathlib import Path

# === Static validations ===
STATIC_TARGETS = [
	("canon/skills.json", "schemas/skills.schema.json"),
	("canon/classes.json", "schemas/classes.schema.json"),
	("canon/titles.json", "schemas/titles.schema.json"),
	("canon/tiers.json", "schemas/tiers.schema.json"),
	("canon/characters/jake/timeline.json", "schemas/character_timeline.schema.json"),
]

def main():
	# Validate all static targets
	for meta_path, schema_path in STATIC_TARGETS:
		p = Path(meta_path)
		s = Path(schema_path)
		if p.exists() and s.exists():
			validate_json_schema(p, s, name=str(p))
		else:
			print(f"⚠️ Skipped missing: {p} or {s}")

	# Validate all known_skills.json files
	for path in Path("canon/characters").rglob("known_skills.json"):
		validate_json_schema(
			data_path=path,
			schema_path=Path("schemas/known_skills.schema.json"),
			name=str(path)
		)

	# Cross-schema consistency checks
	check_known_skills_vs_skills()

if __name__ == "__main__":
	main()
