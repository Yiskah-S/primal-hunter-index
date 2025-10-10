#!/usr/bin/env python3
"""Render the tag registry into a human readable Markdown reference."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CATEGORY_ORDER = [
	"narrative_style",
	"character_tone",
	"scene_function",
	"system_mechanic",
	"power_scaling",
	"lore_topic",
]

CATEGORY_TITLES = {
	"narrative_style": "Narrative Style",
	"character_tone": "Character Tone",
	"scene_function": "Scene Function",
	"system_mechanic": "System Mechanic",
	"power_scaling": "Power Scaling",
	"lore_topic": "Lore Topic",
}


def _strip_comments(payload: str) -> str:
	"""Remove C-style block comments from a JSON-like string."""
	return re.sub(r"/\*.*?\*/", "", payload, flags=re.DOTALL)


def load_registry(registry_path: Path) -> dict:
	text = _strip_comments(registry_path.read_text(encoding="utf-8"))
	return json.loads(text)


def _format_examples(examples: list[dict[str, str]]) -> list[str]:
	lines: list[str] = []
	for entry in examples:
		if not isinstance(entry, dict):
			continue
		scene_id = entry.get("scene_id")
		if not isinstance(scene_id, str):
			continue
		line_number = entry.get("line")
		excerpt = entry.get("excerpt")
		detail_parts: list[str] = [scene_id]
		if isinstance(line_number, int):
			detail_parts.append(f"line {line_number}")
		label = ", ".join(detail_parts)
		if isinstance(excerpt, str) and excerpt.strip():
			lines.append(f"- {label}: {excerpt.strip()}")
		else:
			lines.append(f"- {label}")
	return lines


def render_markdown(registry: dict, source_path: Path) -> str:
	tags = registry.get("tags", [])
	if not isinstance(tags, list):
		raise ValueError("Registry must contain a list of tags under 'tags'.")

	grouped: dict[str, list[dict]] = {}
	for entry in tags:
		if not isinstance(entry, dict):
			continue
		category = entry.get("category")
		if not isinstance(category, str):
			continue
		grouped.setdefault(category, []).append(entry)

	for entries in grouped.values():
		entries.sort(key=lambda t: (t.get("label") or "", t.get("id") or ""))

	lines: list[str] = []
	lines.append("# Tag Registry Reference")
	lines.append("")
	lines.append(f"_Source: `{source_path}`_")
	lines.append("")

	for category in CATEGORY_ORDER:
		entries = grouped.get(category, [])
		if not entries:
			continue
		lines.append(f"## {CATEGORY_TITLES.get(category, category.title())}")
		lines.append("")
		for entry in entries:
			tag_id = entry.get("id", "")
			label = entry.get("label") or tag_id
			lines.append(f"### {label} (`{tag_id}`)")
			lines.append("")

			status = entry.get("status", "unknown")
			allow_inferred = "yes" if entry.get("allow_inferred") else "no"
			scope = entry.get("scope") or []
			scope_text = ", ".join(scope) if scope else "unspecified"

			lines.append(f"- **Status:** {status}")
			lines.append(f"- **Allow inferred:** {allow_inferred}")
			lines.append(f"- **Scope:** {scope_text}")

			definition = entry.get("definition")
			if isinstance(definition, str) and definition.strip():
				lines.append(f"- **Definition:** {definition.strip()}")

			use_when = entry.get("use_when") or []
			if isinstance(use_when, list) and use_when:
				lines.append("- **Use when:**")
				for item in use_when:
					if isinstance(item, str) and item.strip():
						lines.append(f"  - {item.strip()}")

			not_when = entry.get("not_when") or []
			if isinstance(not_when, list) and not_when:
				lines.append("- **Not when:**")
				for item in not_when:
					if isinstance(item, str) and item.strip():
						lines.append(f"  - {item.strip()}")

			instruction = entry.get("generator_instruction")
			if isinstance(instruction, str) and instruction.strip():
				lines.append(f"- **Generator instruction:** {instruction.strip()}")

			aliases = entry.get("aliases") or []
			if isinstance(aliases, list) and aliases:
				alias_text = ", ".join(sorted(str(alias) for alias in aliases if isinstance(alias, str) and alias.strip()))
				if alias_text:
					lines.append(f"- **Aliases:** {alias_text}")

			notes = entry.get("notes")
			if isinstance(notes, str) and notes.strip():
				lines.append(f"- **Notes:** {notes.strip()}")

			examples = entry.get("examples") or []
			if isinstance(examples, list) and examples:
				lines.append("- **Examples:**")
				lines.extend(f"  {line}" for line in _format_examples(examples))

			lines.append("")

	return "\n".join(lines).rstrip() + "\n"


def _safe_relpath(path: Path) -> str:
	cwd = Path.cwd()
	try:
		return str(path.relative_to(cwd))
	except ValueError:
		return str(path)


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="Render tag registry documentation.")
	parser.add_argument(
		"--registry",
		type=Path,
		default=Path("tagging/tag_registry.seed.json"),
		help="Path to the tag registry JSON file (default: %(default)s)",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path("docs/reference/tags.md"),
		help="Path to the generated Markdown file (default: %(default)s)",
	)
	args = parser.parse_args(argv)

	registry = load_registry(args.registry)
	markdown = render_markdown(registry, args.registry)

	args.output.parent.mkdir(parents=True, exist_ok=True)
	args.output.write_text(markdown, encoding="utf-8")
	print(f"✅ Wrote {_safe_relpath(args.output)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
