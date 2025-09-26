#!/usr/bin/env python3
import json
from pathlib import Path
from core.schema_utils import read_json, write_json_atomic, load_schema, validate_instance

SKILLS_FILE = Path("canon/skills.json")
SCHEMA_FILE = Path("schemas/skills.schema.json")

RARITY_MAP = {
	"inf": "Inferior",
	"com": "Common",
	"unc": "Uncommon",
	"rar": "Rare",
	"epi": "Epic",
	"leg": "Legendary",
	"uni": "Unique"
}
RARITY_ENUM = list(RARITY_MAP.values())
STAT_KEYS = ["Str", "Dex", "End", "Agi", "Per", "Vit", "Int", "Wis", "Cha", "Luk"]
LOWER_TO_CANON = {k.lower(): k for k in STAT_KEYS}

def prompt(msg: str, default: str = "") -> str:
	val = input(f"{msg}{f' [{default}]' if default else ''}: ").strip()
	return val or default

def parse_csv_list(raw: str) -> list[str]:
	return [x.strip() for x in raw.split(",") if x.strip()]

def parse_stat_synergy(raw: str) -> dict:
	"""
	Input:  Per:2, Str:1  (stats are case-insensitive; e.g., 'cha' → 'Cha')
	Output: {"Per": 2, "Str": 1}
	"""
	result = {}
	pairs = [p.strip() for p in raw.split(",") if p.strip()]
	for pair in pairs:
		if ":" in pair:
			key, val = pair.split(":", 1)
			key = key.strip()
			key = LOWER_TO_CANON.get(key.lower(), key)  # normalize if known
			try:
				result[key] = int(val.strip())
			except ValueError:
				print(f"⚠️ Invalid stat synergy value for '{key}': '{val}' (must be int)")
	return result

def prompt_resource_cost() -> dict | None:
	if not prompt("Add resource cost? (y/n)", "n").lower().startswith("y"):
		return None
	resource = prompt("Resource name (e.g., Stamina, Mana)")
	if not resource:
		print("⚠️ Skipping resource_cost: no resource given.")
		return None
	act = prompt("Activation cost (number, blank to skip)", "")
	main = prompt("Maintenance cost (number per tick, blank to skip)", "")
	rc_type = prompt("Cost type (e.g., flat, percent-per-second)", "flat")
	obj = {"resource": resource, "type": rc_type}
	if act != "":
		try:
			obj["activation_cost"] = float(act)
		except ValueError:
			print(f"⚠️ Ignoring activation cost '{act}' (not a number)")
	if main != "":
		try:
			obj["maintenance_cost"] = float(main)
		except ValueError:
			print(f"⚠️ Ignoring maintenance cost '{main}' (not a number)")
	return obj

def prompt_rarity() -> str:
	while True:
		raw = prompt("Rarity (Inferior, Common, Uncommon, Rare, Epic, Legendary, Unique)", "Inferior")
		val = raw.strip().capitalize()

		if val in RARITY_ENUM:
			return val

		abbr = raw.strip().lower()[:3]
		if abbr in RARITY_MAP:
			return RARITY_MAP[abbr]

		print(f"❌ Invalid rarity: '{raw}'. Must be one of: {', '.join(RARITY_ENUM)}")


def main():
	schema = load_schema(SCHEMA_FILE)
	skills = read_json(SKILLS_FILE)

	name = prompt("Skill name (canonical, e.g., Identify)")
	if not name:
		print("❌ Aborted: skill name required.")
		return
	if name in skills:
		print(f"❌ Aborted: skill '{name}' already exists.")
		return

	rarity = prompt_rarity()

	skill_type = prompt("Type (e.g., Combat Passive, General Utility, Sensory Passive)", "General Utility")

	class_recs = parse_csv_list(
		prompt("Class recommendations (comma-separated, e.g., Archer, Warrior)", "")
	)

	description = prompt("System description of the skill's core function")

	proficiency = parse_csv_list(
		prompt("Proficiency with? (comma-separated, e.g., bows, crossbows)", "")
	)

	# Retry stat synergy until it's valid
	while True:
		stat_input = prompt(
			"Stat synergy (format: Stat:amount, e.g., Per:2, Str:1 — valid: " + ", ".join(STAT_KEYS) + ")",
			""
		)
		stat_synergy = parse_stat_synergy(stat_input)
		if isinstance(stat_synergy, dict):
			break
		print("❌ Invalid stat synergy format. Try again.")

	passive_benefit = prompt("Passive benefit (optional)", "")

	scene_id = prompt("Scene ID", "01-01-01")
	while True:
		try:
			line = int(prompt("Line number", "0"))
			break
		except ValueError:
			print("❌ Must be an integer.")

	flavor = prompt("Observer (Jake's) opinion / flavor text for the skill")

	behavior = {
		"activation_method": prompt("Activation method", "Focus on target"),
		"deactivation": prompt("Deactivation", "Auto or manual after use"),
		"instinctive_knowledge": prompt("Instinctive knowledge? (y/n)", "y").lower().startswith("y"),
		"user feedback": prompt("Feedback (what the user experiences; paste from canon if desired)", "")
	}

	tags = parse_csv_list(prompt("Tags (comma-separated)", ""))
	granted_by = prompt("Granted by (e.g., 'System Tutorial', 'Class Reward')", "System Tutorial")

	record = {
		"rarity": rarity,
		"type": skill_type,
		"class_recommendations": class_recs,
		"description": description,
		"effects": {
			"proficiency_with": proficiency,
			"stat_synergy": stat_synergy,
			"passive_benefit": passive_benefit
		},
		"first_mentioned_in": {
			"scene_id": scene_id,
			"line": line
		},
		"flavor": flavor,
		"behavior": behavior,
		"tags": tags,
		"granted_by": granted_by
	}

	# Optional: resource cost
	rc = prompt_resource_cost()
	if rc:
		record["resource_cost"] = rc

	# Validate
	validate_instance({name: record}, schema)

	# Save
	skills[name] = record
	write_json_atomic(SKILLS_FILE, skills)
	print(f"✅ Skill '{name}' added to {SKILLS_FILE}")

	# Optional: assign to character
	if prompt("Assign this skill to a character now? (y/n)", "y").lower().startswith("y"):
		import subprocess
		subprocess.run(["python", "cli/assign_skill_to_character.py", name])

if __name__ == "__main__":
	main()
