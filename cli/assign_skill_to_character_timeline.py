#!/usr/bin/env python3
from pathlib import Path

from core.schema_utils import load_schema, read_json, validate_instance, write_json_atomic

SKILLS_FILE = Path("records/skills.json")
SCHEMA_FILE = Path("schemas/character_timeline.schema.json")
CHAR_DIR = Path("records/characters")
SCENE_DIR = Path("records/scene_index")

# ---------- small io helpers ----------


def prompt(msg: str, default: str = "") -> str:
	val = input(f"{msg}{f' [{default}]' if default else ''}: ").strip()
	return val or default


def prompt_retry(msg: str, validate_fn, error_msg: str, default: str = "") -> str:
	while True:
		val = prompt(msg, default)
		if validate_fn(val):
			return val
		print(f"❌ {error_msg}")


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


def prompt_optional_int(msg: str) -> int | None:
	raw = prompt(msg, "")
	if raw == "":
		return None
	try:
		return int(raw)
	except ValueError:
		print("⚠️ Not an integer; ignoring.")
		return None


def parse_csv_list(raw: str) -> list[str]:
	return [x.strip() for x in raw.split(",") if x.strip()]


# ---------- domain helpers ----------


def resolve_scene_id() -> tuple[str, Path]:
	"""
	Ask for a scene_id like '01.02.01', search recursively under records/scene_index.
	Re-prompt until found.
	"""
	while True:
		scene_id = prompt("Scene ID (e.g., 01.02.01)")
		for candidate in {scene_id, scene_id.replace('.', '-')}:
			scene_path = next(SCENE_DIR.rglob(f"{candidate}.json"), None)
			if scene_path and scene_path.exists():
				return scene_id, scene_path
		print(f"❌ scene_id '{scene_id}' not found anywhere under {SCENE_DIR}")


def choose_character() -> str:
	return prompt_retry("Character (folder name, e.g., jake)", lambda v: bool(v), "Character is required.").lower()


def choose_skill(skills: dict) -> str:
	return prompt_retry(
		"Skill name (exact match in skills.json)",
		lambda v: bool(v) and v in skills,
		f"Skill must exist in {SKILLS_FILE}. Use the exact records entry name.",
	)


def choose_nonempty(label: str, default: str = "") -> str:
	return prompt_retry(label, lambda v: bool(v.strip()), "Value is required.", default)


# ---------- main ----------


def main():
	# load catalogs + schema
	skills = read_json(SKILLS_FILE)
	timeline_schema = load_schema(SCHEMA_FILE)

	# inputs with live validation
	character = choose_character()
	skill = choose_skill(skills)
	scene_id, scene_file = resolve_scene_id()
	day = prompt_int("Day learned", default=0, min_val=0)
	source = choose_nonempty("Source (e.g., Level up, Title reward)", "")
	line = prompt_optional_int("Line number (optional)")
	reason = prompt("Reason (optional summary of how skill was acquired)", f"Gained skill: {skill}")
	tags = parse_csv_list(prompt("Tags (comma-sep, optional)", ""))

	# load or create timeline.json for character
	char_dir = CHAR_DIR / character
	timeline_path = char_dir / "timeline.json"
	timeline = read_json(timeline_path)
	if not isinstance(timeline, list):
		print("⚠️ Creating new timeline file.")
		timeline = []

	# find or create a snapshot for this (day, scene_id)
	snap = next((s for s in timeline if s.get("day") == day and s.get("scene_id") == scene_id), None)
	if snap is None:
		snap = {
			"day": day,
			"scene_id": scene_id,
			"source_file": str(scene_file),
			"reason": reason,
			# minimal block to satisfy schema (stats is required with .total)
			"stats": {"total": {}},
		}
		timeline.append(snap)
	else:
		# ensure required fields exist even on older snapshots
		snap.setdefault("stats", {}).setdefault("total", {})
		snap.setdefault("source_file", str(scene_file))
		if "reason" not in snap and reason:
			snap["reason"] = reason

	# add skill to skills[]
	skills_list = snap.setdefault("skills", [])
	if skill not in skills_list:
		skills_list.append(skill)

	# append to skill_log[]
	entry = {"skill": skill, "source": source}
	if line is not None:
		entry["line"] = line
	log = snap.setdefault("skill_log", [])
	log.append(entry)

	# merge tags (dedup)
	if tags:
		existing_tags = snap.setdefault("tags", [])
		existing_tags[:] = list(dict.fromkeys(existing_tags + tags))

	# sort timeline by (day, scene_id)
	timeline.sort(key=lambda s: (s.get("day", 0), s.get("scene_id", "")))

	# validate entire timeline file against schema
	validate_instance(timeline, timeline_schema)

	# persist
	char_dir.mkdir(parents=True, exist_ok=True)
	write_json_atomic(timeline_path, timeline)
	print(f"✅ Skill '{skill}' assigned to {character} on day {day} ({scene_id}) → {timeline_path}")


if __name__ == "__main__":
	main()
