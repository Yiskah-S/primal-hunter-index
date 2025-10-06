#!/usr/bin/env python3
"""
Promote cleaned tag candidates into tag_registry.json.
Handles casing, punctuation, and messy human input.

Usage:
  python -m tools.promote_tags --all [--commit]
  python -m tools.promote_tags --grep "viper" --commit
  python -m tools.promote_tags --ids skills.basic_archery,scene_type.romantic_scene
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

from core.io_safe import write_json_atomic
from core.schema_utils import validate_json_file

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = REPO_ROOT / "tagging" / "tag_candidates.json"
REGISTRY = REPO_ROOT / "tagging" / "tag_registry.json"
SCHEMA = REPO_ROOT / "schemas" / "tag_registry.schema.json"


def load_json(path: Path) -> dict:
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Promote reviewed tags to registry.")
	grp = p.add_mutually_exclusive_group(required=True)
	grp.add_argument("--all", action="store_true", help="Promote all entries.")
	grp.add_argument("--ids", type=str, help="Comma-separated list like 'skills.foo,scene_type.bar'")
	grp.add_argument("--grep", type=str, help="Regex match on tag IDs.")
	p.add_argument("--commit", action="store_true", help="Actually write changes.")
	p.add_argument("--backup", action="store_true", help="Backup registry before overwrite.")
	return p.parse_args()


def slugify(text: str) -> str:
	"""Turn 'Blood of the Malefic Viper' → 'blood_of_the_malefic_viper'"""
	text = unicodedata.normalize("NFKD", text)
	text = re.sub(r"[’']", "", text)  # remove apostrophes
	text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
	text = re.sub(r"_+", "_", text)
	return text.strip("_").lower()


def normalize_section(section: str) -> str:
	return slugify(section)


def normalize_candidates(raw: dict) -> list[tuple[str, str, str]]:
	"""Returns list of (section, original, slug) tuples"""
	cleaned = []
	for raw_section, values in raw.items():
		section = normalize_section(raw_section)
		for entry in values:
			if isinstance(entry, str):
				original = entry.strip()
				slug = slugify(original)
				cleaned.append((section, original, slug))
	return cleaned


def filter_ids(all_tags: list[tuple[str, str, str]], args: argparse.Namespace) -> list[tuple[str, str, str]]:
	if args.all:
		return all_tags

	if args.ids:
		targets = [s.strip() for s in args.ids.split(",")]
		return [t for t in all_tags if f"{t[0]}.{t[2]}" in targets]

	if args.grep:
		pat = re.compile(args.grep)
		return [t for t in all_tags if pat.search(f"{t[0]}.{t[2]}")]

	return []


def promote_object(section: str, original: str, slug: str) -> dict:
	return {
		"tag_id": f"tag.{section}.{slug}",
		"tag": slug,
		"type": section,
		"tag_role": "heuristic",
		"status": "candidate",
		"approved": False,
		"allow_inferred": False,
		"description": original,
		"source": "manual_review",
		"notes": "Promoted from tag_candidates.json"
	}


def merge_into_registry(existing: dict, new_objs: list[dict]) -> dict:
	merged = dict(existing)
	added = 0

	for obj in new_objs:
		section = obj["type"]
		tag_id = obj["tag_id"]

		if section not in merged:
			merged[section] = []

		if any(t["tag_id"] == tag_id for t in merged[section]):
			continue

		merged[section].append(obj)
		added += 1

	print(f"Prepared {added} new tags for promotion.")
	return merged


def main():
	args = parse_args()
	candidates = load_json(CANDIDATES)
	registry = load_json(REGISTRY)

	all_clean = normalize_candidates(candidates)
	selected = filter_ids(all_clean, args)

	if not selected:
		print("No matching tags found.")
		return

	# Build tag objects
	to_promote = [promote_object(sec, orig, slug) for sec, orig, slug in selected]
	new_registry = merge_into_registry(registry, to_promote)

	# Validate output before writing
	validate_json_file(new_registry, SCHEMA)

	if args.commit:
		write_json_atomic(REGISTRY, new_registry, make_backup=args.backup)
		print(f"Committed {len(to_promote)} new tags.")
	else:
		print(f"Dry-run: would add {len(to_promote)} new tags:")
		for _, original, slug in selected:
			print(f"  {original} → {slug}")
