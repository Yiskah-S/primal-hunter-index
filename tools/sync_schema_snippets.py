#!/usr/bin/env python3
"""Synchronise JSON schema snippets embedded in Markdown contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

MARKER_PATTERNS = [
	re.compile(r"Drop into `([^`]+)`"),
	re.compile(r"Embed in `([^`]+)`"),
]


@dataclass
class MarkerMatch:
	schema_path: Path
	code_start: int
	code_end: int


def _find_marker(line: str, repo_root: Path) -> Path | None:
	for pattern in MARKER_PATTERNS:
		match = pattern.search(line)
		if match:
			relative = Path(match.group(1))
			if relative.is_absolute():
				return relative
			return (repo_root / relative).resolve()
	return None


def _dump_schema(schema_path: Path) -> list[str]:
	data = json.loads(schema_path.read_text(encoding="utf-8"))
	text = json.dumps(data, indent=2, ensure_ascii=False)
	return text.splitlines()


def _locate_code_block(lines: list[str], start_index: int) -> tuple[int, int] | None:
	code_start = None
	for idx in range(start_index + 1, len(lines)):
		line = lines[idx].strip()
		if line.startswith("```"):
			if code_start is None and line.startswith("```json"):
				code_start = idx
			elif code_start is not None:
				return code_start, idx
	return None


def sync_document(doc_path: Path, *, check: bool = False, repo_root: Path = REPO_ROOT) -> bool:
	lines = doc_path.read_text(encoding="utf-8").splitlines()
	changed = False
	idx = 0
	while idx < len(lines):
		schema_path = _find_marker(lines[idx], repo_root)
		if schema_path is None:
			idx += 1
			continue
		if not schema_path.exists():
			raise FileNotFoundError(f"{doc_path}: referenced schema missing: {schema_path}")
		block_bounds = _locate_code_block(lines, idx)
		if block_bounds is None:
			raise ValueError(f"{doc_path}: unable to locate code block after schema marker near line {idx + 1}")
		code_start, code_end = block_bounds
		new_block = _dump_schema(schema_path)
		existing_block = lines[code_start + 1 : code_end]
		if existing_block != new_block:
			changed = True
			if not check:
				lines[code_start + 1 : code_end] = new_block
				idx = code_start + 1 + len(new_block) + 1
				continue
		idx = code_end + 1
	if changed and not check:
		doc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
	return changed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Synchronise schema snippets inside Markdown docs.")
	parser.add_argument(
		"--docs-root",
		type=Path,
		default=DOCS_ROOT,
		help="Docs directory to scan (default: %(default)s)",
	)
	parser.add_argument(
		"--check",
		action="store_true",
		help="Do not write changes; exit non-zero if updates are needed.",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	changes_detected = False
	for md_path in sorted(args.docs_root.rglob("*.md")):
		try:
			if sync_document(md_path, check=args.check, repo_root=REPO_ROOT):
				changes_detected = True
				if not args.check:
					print(f"🔄 Updated snippet in {md_path.relative_to(REPO_ROOT)}")
		except (FileNotFoundError, ValueError) as exc:
			print(f"❌ {exc}")
			return 1

	if args.check and changes_detected:
		print("❌ Schema snippets are out of sync.")
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())
