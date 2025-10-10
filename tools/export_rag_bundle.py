#!/usr/bin/env python3
"""Generate retrieval bundles for downstream RAG pipelines."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from core.schema_utils import load_schema, read_json, validate_instance

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = REPO_ROOT / "records"
SCENE_INDEX_ROOT = RECORDS_ROOT / "scene_index"
CHARACTER_ROOT = RECORDS_ROOT / "characters"
SCHEMA_PATH = REPO_ROOT / "schemas" / "export_bundle.schema.json"
BUNDLE_FILENAMES = {
	"style": "bundle_style.jsonl",
	"mechanics": "bundle_mechanics.jsonl",
	"story": "bundle_story.jsonl",
}


def _relative(path: Path) -> str:
	try:
		return str(path.relative_to(REPO_ROOT))
	except ValueError:
		return str(path)


def _anchor_hash(*components: str) -> str:
	data = "::".join(components).encode("utf-8")
	return hashlib.blake2s(data, digest_size=12).hexdigest()


def _read_scene_files(scene_root: Path) -> list[dict[str, Any]]:
	scenes: list[dict[str, Any]] = []
	if not scene_root.exists():
		return scenes
	for path in sorted(scene_root.rglob("*.json")):
		if path.name.endswith(".meta.json"):
			continue
		scene = read_json(path)
		if isinstance(scene, dict) and "scene_id" in scene:
			scenes.append(scene)
	return scenes


def _collect_timeline_entries(records_root: Path) -> list[tuple[str, dict[str, Any]]]:
	entries: list[tuple[str, dict[str, Any]]] = []
	candidate_dirs: list[Path] = []
	characters_dir = records_root / "characters"
	if characters_dir.exists():
		candidate_dirs.append(characters_dir)
	else:
		candidate_dirs.append(records_root)

	for base_dir in candidate_dirs:
		for timeline_path in sorted(base_dir.glob("*/timeline.json")):
			if not timeline_path.is_file():
				continue
			timeline = read_json(timeline_path)
			if not isinstance(timeline, list):
				continue
			character = timeline_path.parent.name
			for event in timeline:
				if isinstance(event, dict):
					entries.append((character, event))
	return entries


def _build_scene_provenance(scene: dict[str, Any]) -> list[dict[str, Any]]:
	return [
		{
			"type": "scene",
			"scene_id": scene.get("scene_id"),
			"line_start": scene.get("start_line"),
			"line_end": scene.get("end_line"),
		}
	]


def _first_source_ref(entry: dict[str, Any]) -> dict[str, Any] | None:
	source_ref = entry.get("source_ref")
	if isinstance(source_ref, list) and source_ref:
		first = source_ref[0]
		return first if isinstance(first, dict) else None
	if isinstance(source_ref, dict):
		return source_ref
	return None


def _ensure_tags(values: Iterable[str]) -> list[str]:
	seen: dict[str, None] = {}
	for value in values:
		if not isinstance(value, str):
			continue
		value = value.strip()
		if value and value not in seen:
			seen[value] = None
	return list(seen.keys())


def _build_style_rows(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
	rows: list[dict[str, Any]] = []
	for scene in scenes:
		scene_id = scene.get("scene_id")
		if not isinstance(scene_id, str):
			continue
		title = scene.get("title", "")
		mood = _ensure_tags(scene.get("mood", []))
		text_parts = [f"{title}".strip(), f"Mood: {', '.join(mood)}" if mood else "", scene.get("summary", "")]
		text = "\n".join(part for part in text_parts if part)
		if not text:
			continue
		start_line = scene.get("start_line")
		end_line = scene.get("end_line")
		if not isinstance(start_line, int) or not isinstance(end_line, int):
			continue
		row = {
			"id": f"style.{scene_id}",
			"text": text,
			"span": {
				"scene_id": scene_id,
				"line_start": start_line,
				"line_end": end_line,
				"anchor_hash": _anchor_hash(scene_id, "style", str(start_line), str(end_line)),
			},
			"weights": {"certainty": 1.0, "tone": 0.9, "mechanics": 0.15},
			"tags": _ensure_tags(mood + ["style"]),
			"source_ids": [f"scene:{scene_id}"],
			"provenance": _build_scene_provenance(scene),
		}
		rows.append(row)
	return rows


def _build_story_rows(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
	rows: list[dict[str, Any]] = []
	for scene in scenes:
		scene_id = scene.get("scene_id")
		summary = scene.get("summary")
		if not isinstance(scene_id, str) or not isinstance(summary, str) or not summary.strip():
			continue
		start_line = scene.get("start_line")
		end_line = scene.get("end_line")
		if not isinstance(start_line, int) or not isinstance(end_line, int):
			continue
		row = {
			"id": f"story.{scene_id}",
			"text": summary.strip(),
			"span": {
				"scene_id": scene_id,
				"line_start": start_line,
				"line_end": end_line,
				"anchor_hash": _anchor_hash(scene_id, "story", str(start_line), str(end_line)),
			},
			"weights": {"certainty": 1.0, "tone": 0.6, "mechanics": 0.4},
			"tags": _ensure_tags(scene.get("tags", [])),
			"source_ids": [f"scene:{scene_id}"],
			"provenance": _build_scene_provenance(scene),
		}
		rows.append(row)
	return rows


def _build_mechanics_rows(entries: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
	rows: list[dict[str, Any]] = []
	for character, entry in entries:
		source = _first_source_ref(entry)
		if not source:
			continue
		scene_id = source.get("scene_id")
		line_start = source.get("line_start")
		line_end = source.get("line_end")
		if not isinstance(scene_id, str) or not isinstance(line_start, int) or not isinstance(line_end, int):
			continue

		notes = entry.get("notes") or entry.get("reason") or ""
		skills = entry.get("skills") or []
		equipment = entry.get("equipment") or []
		stats = entry.get("stats", {})

		text_sections: list[str] = []
		if notes:
			text_sections.append(notes.strip())
		if skills:
			text_sections.append("Skills: " + ", ".join(str(skill) for skill in skills))
		if equipment:
			text_sections.append("Equipment: " + ", ".join(str(item) for item in equipment))
		if isinstance(stats, dict) and stats.get("total"):
			total_stats = stats["total"]
			if isinstance(total_stats, dict):
				stat_line = ", ".join(f"{k}: {v}" for k, v in total_stats.items())
				if stat_line:
					text_sections.append(f"Stats: {stat_line}")
		if not text_sections:
			continue

		tags = _ensure_tags(entry.get("tags", []))
		row = {
			"id": f"mechanics.{character}.{scene_id}.{len(rows) + 1}",
			"text": "\n".join(text_sections),
			"span": {
				"scene_id": scene_id,
				"line_start": line_start,
				"line_end": line_end,
				"anchor_hash": _anchor_hash(scene_id, "mechanics", str(line_start), str(line_end)),
			},
			"weights": {"certainty": 0.85, "tone": 0.2, "mechanics": 0.95},
			"tags": _ensure_tags(tags + ["mechanics", f"character-{character}"]),
			"source_ids": [f"timeline:{character}", f"scene:{scene_id}"],
			"provenance": [source],
		}
		rows.append(row)
	return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]], schema: dict[str, Any] | None) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as handle:
		for row in rows:
			if schema is not None:
				validate_instance(row, schema)
			handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Export scene and timeline data into JSONL bundles.")
	parser.add_argument(
		"--records-root",
		type=Path,
		default=RECORDS_ROOT,
		help="Root directory containing the records dataset (default: %(default)s)",
	)
	parser.add_argument(
		"--output-dir",
		type=Path,
		default=REPO_ROOT / "__sandbox__" / "bundles",
		help="Directory to write JSONL bundles (default: %(default)s)",
	)
	parser.add_argument(
		"--no-validate",
		action="store_true",
		help="Skip validating rows against schemas/export_bundle.schema.json",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	scenes = _read_scene_files(args.records_root / "scene_index")
	timeline_entries = _collect_timeline_entries(args.records_root)

	if not scenes:
		print("⚠️  No scenes found; bundles will be empty.")
	if not timeline_entries:
		print("⚠️  No timeline entries found; mechanics bundle may be empty.")

	rows = {
		"style": _build_style_rows(scenes),
		"story": _build_story_rows(scenes),
		"mechanics": _build_mechanics_rows(timeline_entries),
	}

	schema = None if args.no_validate else load_schema(SCHEMA_PATH)

	for bundle_name, filename in BUNDLE_FILENAMES.items():
		out_path = args.output_dir / filename
		_write_jsonl(out_path, rows[bundle_name], schema)
		print(f"✅ Wrote {len(rows[bundle_name])} rows to {_relative(out_path)}")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
