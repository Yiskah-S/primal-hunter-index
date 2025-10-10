#!/usr/bin/env python3
"""Check Markdown documents for broken internal links."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
REFERENCE_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)
REFERENCE_USE_RE = re.compile(r"\[([^\]]+)\]\[([^\]]+)\]")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "data:")


def _resolve_reference_links(text: str) -> dict[str, str]:
	return {key: target for key, target in REFERENCE_DEF_RE.findall(text)}


def _normalize_link(link: str) -> str:
	return link.strip().strip("<>")


def _resolve_target(link: str, current_file: Path) -> Path | None:
	link = _normalize_link(link)
	if not link or link.startswith("#") or link.startswith(EXTERNAL_PREFIXES):
		return None

	path_part = link.split("#", 1)[0]
	if not path_part:
		return None

	if path_part.startswith("/"):
		candidate = (REPO_ROOT / path_part.lstrip("/")).resolve()
	else:
		candidate = (current_file.parent / path_part).resolve()
	return candidate


def _relative(path: Path) -> str:
	try:
		return str(path.relative_to(REPO_ROOT))
	except ValueError:
		return str(path)


def collect_broken_links(docs_root: Path) -> list[str]:
	errors: list[str] = []
	for md_path in sorted(docs_root.rglob("*.md")):
		text = md_path.read_text(encoding="utf-8")
		references = _resolve_reference_links(text)

		def _record(target: str, label: str) -> None:
			target_path = _resolve_target(target, md_path)
			if target_path is None:
				return
			if not target_path.exists():
				errors.append(
					f"{_relative(md_path)}: link '{label}' points to missing file '{_relative(target_path)}'"
				)

		for label, target in INLINE_LINK_RE.findall(text):
			_record(target, label)

		for label, ref in REFERENCE_USE_RE.findall(text):
			target = references.get(ref)
			if target is None:
				errors.append(f"{_relative(md_path)}: reference '{ref}' used for '{label}' is undefined")
				continue
			_record(target, label)
	return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Check docs/ for broken relative Markdown links.")
	parser.add_argument(
		"--docs-root",
		type=Path,
		default=DOCS_ROOT,
		help="Directory containing documentation Markdown files (default: %(default)s)",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	errors = collect_broken_links(args.docs_root)
	for error in errors:
		print(f"❌ {error}")
	return 1 if errors else 0


if __name__ == "__main__":
	sys.exit(main())
