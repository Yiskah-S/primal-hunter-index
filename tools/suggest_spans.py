#!/usr/bin/env python3
"""Suggest low-certainty quote spans for a given skill identifier.

The goal is to give authors a quick starting point when wiring up
`source_ref[]` entries. Suggestions are intentionally conservative:
they rely on scene_index summaries and skill lists, and mark each
candidate with `certainty: low` and `status: pending`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
import json

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENE_INDEX_ROOT = REPO_ROOT / "records" / "scene_index"


def _skill_terms(skill_id: str) -> list[str]:
	slug = skill_id.split(".", 1)[-1]
	slug = slug.replace(".", " ")
	words = slug.replace("_", " ").strip()
	if not words:
		return []
	return list({words.lower(), words.title(), words.upper()})


def _iter_scene_files(root: Path) -> list[Path]:
	if not root.exists():
		return []
	return sorted(path for path in root.rglob("*.json") if path.is_file() and not path.name.endswith(".meta.json"))


def _load_scene(path: Path) -> dict[str, Any]:
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
	except FileNotFoundError:
		return {}
	except json.JSONDecodeError:
		return {}
	return data if isinstance(data, dict) else {}


def _matches_scene(scene: dict[str, Any], terms: list[str]) -> bool:
	summary = scene.get("summary", "")
	title = scene.get("title", "")
	skills = scene.get("skills_gained", [])

	def _text_contains(text: str) -> bool:
		text_l = text.lower()
		return any(term.lower() in text_l for term in terms)

	if isinstance(summary, str) and _text_contains(summary):
		return True
	if isinstance(title, str) and _text_contains(title):
		return True
	if isinstance(skills, list):
		for value in skills:
			if isinstance(value, str) and _text_contains(value):
				return True
	return False


def suggest_spans(skill_id: str, limit: int | None = None) -> list[dict[str, Any]]:
	terms = _skill_terms(skill_id)
	if not terms:
		return []

	suggestions: list[dict[str, Any]] = []
	for scene_file in _iter_scene_files(SCENE_INDEX_ROOT):
		scene = _load_scene(scene_file)
		if not scene:
			continue
		if not _matches_scene(scene, terms):
			continue

		scene_id = scene.get("scene_id")
		start_line = scene.get("start_line")
		end_line = scene.get("end_line")
		if not isinstance(scene_id, str):
			continue
		if not isinstance(start_line, int) or not isinstance(end_line, int):
			start_line = 1
			end_line = 1

		suggestions.append(
			{
				"skill_id": skill_id,
				"scene_id": scene_id,
				"line_start": start_line,
				"line_end": end_line,
				"certainty": "low",
				"status": "pending",
				"basis": "Matched scene summary/title/skills_gained",
			}
		)
		if limit and len(suggestions) >= limit:
			break
	return suggestions


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Suggest low-certainty spans for a skill identifier.")
	parser.add_argument("--skill", required=True, help="Skill identifier (e.g., sn.basic_archery).")
	parser.add_argument(
		"--limit",
		type=int,
		default=5,
		help="Maximum number of suggestions to emit (default: %(default)s).",
	)
	parser.add_argument(
		"--output",
		type=Path,
		help="Optional path to write suggestions as JSON. Defaults to stdout.",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	suggestions = suggest_spans(args.skill, limit=args.limit)
	payload = {"skill_id": args.skill, "suggestions": suggestions}

	if args.output:
		args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
		print(f"✅ Wrote {args.output}")
	else:
		print(json.dumps(payload, indent=2))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
