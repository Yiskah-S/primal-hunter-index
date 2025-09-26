#!/usr/bin/env python3
import json
from pathlib import Path
from core.schema_utils import read_json, write_json_atomic, load_schema, validate_instance

SKILLS_FILE = Path("canon/skills.json")
SCHEMA_FILE = Path("schemas/skills.schema.json")

RARITY_ENUM = ["Inferior", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Unique"]
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

	rarity = prompt("Rarity (Inferior, Common, Uncommon, Rare, Epic, Legendary, Unique)", "Inferior")
	if rarity not in RARITY_ENUM:
		print(f"❌ Invalid rarity. Must be one of: {', '.join(RARITY_ENUM)}")
		return

	record = {
		"rarity": rarity,
		"type": prompt("Type (e.g., Combat Passive, General Utility, Sensory Passive)", "General Utility"),
		"class_recommendations": parse_csv_list(
			prompt("Class recommendations (comma-separated, e.g., Archer, Warrior)", "")
		),
		"description": prompt("System description of the skill's core function"),
		"effects": {
			"proficiency_with": parse_csv_list(
				prompt("Proficiency with? (comma-separated, e.g., bows, crossbows)", "")
			),
			"stat_synergy": parse_stat_synergy(
				prompt(
					"Stat synergy (format: Stat:amount, ... e.g., Per:2, Str:1; valid stats: " +
					", ".join(STAT_KEYS) + ")",
					""
				)
			),
			"passive_benefit": prompt("Passive benefit (optional)", "")
		},
		"first_mentioned_in": {
			"scene_id": prompt("Scene ID", "01-01-01"),
			"line": int(prompt("Line number", "0"))
		},
		"flavor": prompt("Observer (Jake's) opinion / flavor text for the skill"),
		"behavior": {
			"activation_method": prompt("Activation method", "Focus on target"),
			"deactivation": prompt("Deactivation", "Auto or manual after use"),
			"instinctive_knowledge": prompt("Instinctive knowledge? (y/n)", "y").lower().startswith("y"),
			"feedback": prompt("Feedback (what the user experiences; paste from canon if desired)", "")
		},
		"tags": parse_csv_list(prompt("Tags (comma-separated)", "")),
		"granted_by": prompt("Granted by (e.g., 'System Tutorial', 'Class Reward')", "System Tutorial")
	}

	rc = prompt_resource_cost()
	if rc:
		record["resource_cost"] = rc

	validate_instance({name: record}, schema)

	skills[name] = record
	write_json_atomic(SKILLS_FILE, skills)
	print(f"✅ Skill '{name}' added to {SKILLS_FILE}")

if __name__ == "__main__":
	main()
