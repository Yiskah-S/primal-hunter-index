import os
import json
from pathlib import Path

METADATA_DIR = Path("metadata")
METADATA_DIR.mkdir(exist_ok=True)

# Define target files and their empty schema
files_and_templates = {
	"races.json": {},
	"classes.json": {},
	"tiers.json": {},
	"titles.json": {},
	"skills.json": {},
	"stat_scaling.json": {},
	"system_glossary.json": {},
	"chapters_to_posts.json": {},  # Already in use — included for consistency
	"global_announcement_log.json": [],
	"known_skills.json": {},
	"zone_lore.json": {}
}

def create_metadata_files():
	for fname, template in files_and_templates.items():
		fpath = METADATA_DIR / fname
		if fpath.exists():
			print(f"⚠️  Skipping existing: {fname}")
			continue

		with open(fpath, "w", encoding="utf-8") as f:
			json.dump(template, f, indent=4)
		print(f"✅ Created: {fname}")

if __name__ == "__main__":
	create_metadata_files()
