#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from core.schema_utils import read_json, write_json_atomic, load_schema, validate_instance

SKILLS_FILE = Path("canon/skills.json")
SCHEMA_FILE = Path("schemas/skills.schema.json")
SCENES_DIR = Path("canon/scene_index")

# --- enums / maps -------------------------------------------------------------

RARITY_MAP = {
	"inf": "Inferior",
	"com": "Common",
	"unc": "Uncommon",
	"rar": "Rare",
	"epi": "Epic",
	"leg": "Legendary",
	"uni": "Unique",
}
RARITY_ENUM = list(RARITY_MAP.values())

STAT_KEYS = ["Str", "Dex", "End", "Agi", "Per", "Vit", "Int", "Wis", "Cha", "Luk"]
LOWER_TO_CANON = {k.lower(): k for k in STAT_KEYS}

# --- small io helpers ---------------------------------------------------------

def prompt(msg: str, default: str = "") -> str:
	val = input(f"{msg}{f' [{default}]' if default else ''}: ").strip()
	return val or default

def prompt_retry(msg: str, validate_fn, error_msg: str, default: str = "") -> str:
	while True:
		val = prompt(msg, default)
		if validate_fn(val):
			return val
		print(f"❌ {error_msg}")

def prompt_yes_no(msg: str, default_yes: bool = True) -> bool:
	d = "y" if default_yes else "n"
	return prompt(msg, d).lower().startswith("y")

def prompt_int(msg: str, default: int | None = None, min_val: int | None = None, max_val: int | None = None) -> int:
	default_str = "" if default is None else str(default)
	while True:
		raw = prompt(msg, default_str)
		try:
			val = int(raw)
		except ValueError:
			print("❌ Must be an integer.")
			continue
		if min_val is not None and val < min_val:
			print(f"❌ Must be ≥ {min_val}.")
			continue
		if max_val is not None and val > max_val:
			print(f"❌ Must be ≤ {max_val}.")
			continue
		return val

# --- parsing helpers ----------------------------------------------------------

def parse_csv_list(raw: str) -> list[str]:
	return [x.strip() for x in raw.split(",") if x.strip()]

def parse_stat_synergy(raw: str) -> dict:
	"""
	Input example:  Per:2, Str:1  (case-insensitive keys; e.g., 'cha' → 'Cha')
	Returns: {"Per": 2, "Str": 1}
	Warns and skips malformed pairs.
	"""
	result: dict[str, int] = {}
	if not raw.strip():
		return result

	for pair in [p.strip() for p in raw.split(",") if p.strip()]:
		if ":" not in pair:
			print(f"⚠️ Skipping '{pair}' — expected format Stat:amount")
			continue
		key, val = pair.split(":", 1)
		key = key.strip()
		key = LOWER_TO_CANON.get(key.lower(), key)
		if key not in STAT_KEYS:
			print(f"⚠️ Skipping unknown stat '{key}' — must be one of: {', '.join(STAT_KEYS)}")
			continue
		try:
			num = int(val.strip())
		except ValueError:
			print(f"⚠️ Skipping '{pair}' — amount must be an integer")
			continue
		result[key] = num
	return result

def prompt_stat_synergy() -> dict:
	while True:
		raw = prompt(f"Stat synergy (format: Stat:amount, e.g., Per:2, Str:1 — valid: {', '.join(STAT_KEYS)})", "")
		result = parse_stat_synergy(raw)
		# Always a dict; we already warn and skip bad pairs.
		return result

def prompt_rarity() -> str:
	while True:
		raw = prompt("Rarity (Inferior, Common, Uncommon, Rare, Epic, Legendary, Unique)", "Inferior").strip()
		# full match
		if raw.capitalize() in RARITY_ENUM:
			return raw.capitalize()
		# abbr match (first 3 letters)
		abbr = raw.lower()[:3]
		if abbr in RARITY_MAP:
			return RARITY_MAP[abbr]
		print(f"❌ Invalid rarity: '{raw}'. Must be one of: {', '.join(RARITY_ENUM)}")

def prompt_scene_id() -> tuple[str, Path]:
	"""
	Resolves a scene_id like '01-01-01' anywhere under canon/scene_index/**.
	"""
	while True:
		scene_id = prompt("Scene ID", "01-01-01")
		scene_file = next(SCENES_DIR.rglob(f"{scene_id}.json"), None)
		if scene_file and scene_file.exists():
			return scene_id, scene_file
		print(f"❌ scene_id '{scene_id}' not found under {SCENES_DIR} (searched recursively).")

def build_resource_cost() -> dict | None:
	if not prompt_yes_no("Add resource cost? (y/n)", default_yes=False):
		return None
	resource = prompt("Resource name (e.g., Stamina, Mana)")
	if not resource:
		print("⚠️ Skipping resource_cost: no resource given.")
		return None

	rc_type = prompt("Cost type (e.g., flat, percent-per-second)", "flat")
	act_raw = prompt("Activation cost (number, blank to skip)", "")
	main_raw = prompt("Maintenance cost (number per tick, blank to skip)", "")

	obj: dict = {"resource": resource, "type": rc_type}
	if act_raw:
		try:
			obj["activation_cost"] = float(act_raw)
		except ValueError:
			print(f"⚠️ Ignoring activation cost '{act_raw}' (not a number)")
	if main_raw:
		try:
			obj["maintenance_cost"] = float(main_raw)
		except ValueError:
			print(f"⚠️ Ignoring maintenance cost '{main_raw}' (not a number)")
	return obj

# --- main flow ----------------------------------------------------------------

def main():
	# Load schema & current skills
	schema = load_schema(SCHEMA_FILE)
	skills = read_json(SKILLS_FILE)

	# Name (unique, non-empty)
	name = prompt_retry(
		"Skill name (canonical, e.g., Identify)",
		lambda v: bool(v) and v not in skills,
		"Skill name is required and must not already exist."
	)

	# Core fields (validated at input time)
	rarity = prompt_rarity()
	skill_type = prompt("Type (e.g., Combat Passive, General Utility, Sensory Passive)", "General Utility")
	class_recs = parse_csv_list(prompt("Class recommendations (comma-separated, e.g., Archer, Warrior)", ""))
	description = prompt("System description of the skill's core function")
	proficiency = parse_csv_list(prompt("Proficiency with? (comma-separated, e.g., bows, crossbows)", ""))

	stat_synergy = prompt_stat_synergy()
	passive_benefit = prompt("Passive benefit (optional)", "")

	scene_id, _scene_file = prompt_scene_id()
	line = prompt_int("Line number", default=0, min_val=0)

	flavor = prompt("Flavor text / observer opinion")

	behavior = {
		"activation_method": prompt("Activation method", "Focus on target"),
		"deactivation": prompt("Deactivation", "Auto or manual after use"),
		"instinctive_knowledge": prompt_yes_no("Instinctive knowledge? (y/n)", True),
		# IMPORTANT: schema key is 'feedback', not 'user feedback'
		"feedback": prompt("Feedback (what the user experiences; paste from canon if desired)", "")
	}

	tags = parse_csv_list(prompt("Tags (comma-separated)", ""))
	granted_by = prompt("Granted by (e.g., 'System Tutorial', 'Class Reward')", "System Tutorial")

	# Assemble record
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

	# Optional resource cost (validated by schema at the end)
	rc = build_resource_cost()
	if rc:
		record["resource_cost"] = rc

	# Preview & confirm before saving
	print("\n— Preview —")
	print(json.dumps({name: record}, indent=2))
	if not prompt_yes_no("Save this skill? (y/n)", True):
		print("❌ Aborted.")
		return

	# Final schema validation (safety net)
	try:
		validate_instance({name: record}, schema)
	# If you want to be extra nice: parse and highlight path/message here.
	except Exception as e:
		print("❌ Schema validation failed:\n")
		print(e)
		return

	# Persist
	skills[name] = record
	write_json_atomic(SKILLS_FILE, skills)
	print(f"✅ Skill '{name}' added to {SKILLS_FILE}")

	# Optional: chain to timeline assignment
	if prompt_yes_no("Assign this skill to a character timeline now? (y/n)", True):
		try:
			# Opens the interactive assigner (keeps UX simple & decoupled)
			subprocess.run(["python", "cli/assign_skill_to_character_timeline.py"], check=True)
		except subprocess.CalledProcessError as e:
			print(f"⚠️ Error launching assigner: {e}")

if __name__ == "__main__":
	main()
