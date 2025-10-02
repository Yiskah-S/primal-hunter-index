#!/usr/bin/env python3
"""Copy chapter files mentioning one or more keywords into a review bundle.

This helper mirrors the `chapters/Book XX` layout under an output folder so you
can review every excerpt that mentions a given skill/term. A JSON manifest is
emitted alongside the copied files containing the line numbers (and optional
context excerpts) for each match.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

SUPPORTED_EXTENSIONS = {".md", ".txt"}


@dataclass
class MatchRecord:
    line: int
    excerpt: str


def slugify(value: str) -> str:
    """Convert a string into a filesystem-friendly slug."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower() or "search"


def iter_text_files(root: Path, extensions: Iterable[str]) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in extensions:
            yield path


def build_excerpts(lines: Sequence[str], matches: Sequence[int], context: int) -> list[MatchRecord]:
    records: list[MatchRecord] = []
    if context <= 0:
        for idx in matches:
            records.append(MatchRecord(line=idx, excerpt=lines[idx - 1].rstrip()))
        return records

    total = len(lines)
    for idx in matches:
        start = max(0, idx - 1 - context)
        end = min(total, idx + context)
        excerpt_lines = [line.rstrip() for line in lines[start:end]]
        excerpt = "\n".join(excerpt_lines)
        records.append(MatchRecord(line=idx, excerpt=excerpt))
    return records


def search_and_copy(
    chapters_root: Path,
    output_root: Path,
    keywords: Sequence[str],
    use_regex: bool,
    context_lines: int,
    extensions: set[str],
    slug: str | None,
) -> int:
    if not chapters_root.is_dir():
        raise FileNotFoundError(f"Chapters root not found: {chapters_root}")

    keyword_mode = "regex" if use_regex else "keywords"
    if use_regex:
        pattern = re.compile(keywords[0], re.IGNORECASE)
    else:
        lowered = [kw.lower() for kw in keywords]
        pattern = None

    slug_value = slug or slugify("_".join(keywords))
    destination_root = output_root / slug_value
    destination_root.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, dict] = {}
    matches_found = 0

    for file_path in iter_text_files(chapters_root, extensions):
        with file_path.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()

        line_hits: list[int] = []
        for idx, line in enumerate(lines, start=1):
            haystack = line.rstrip()
            if use_regex:
                if pattern.search(haystack):
                    line_hits.append(idx)
            else:
                lowered_line = haystack.lower()
                if any(keyword in lowered_line for keyword in lowered):
                    line_hits.append(idx)

        if not line_hits:
            continue

        relative_path = file_path.relative_to(chapters_root)
        destination_path = destination_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file_path, destination_path)

        excerpts = build_excerpts(lines, line_hits, context_lines)
        manifest[relative_path.as_posix()] = {
            "relative_path": relative_path.as_posix(),
            "matches": [
                {
                    "line": record.line,
                    "excerpt": record.excerpt,
                }
                for record in excerpts
            ],
            "keyword_mode": keyword_mode,
            "keywords": keywords,
        }
        matches_found += 1

    manifest_path = destination_root / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)

    return matches_found


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy chapter files containing keywords to a review folder.")
    parser.add_argument(
        "keywords",
        nargs="+",
        help="Keyword(s) to search for. Use --regex to treat the first argument as a regular expression.",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat the first keyword as a regular expression (remaining positional keywords are ignored).",
    )
    parser.add_argument(
        "--chapters-root",
        type=Path,
        default=Path("chapters"),
        help="Root directory containing chapter files (default: chapters/).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("search_results"),
        help="Directory where result bundles are written (default: search_results/).",
    )
    parser.add_argument(
        "--slug",
        type=str,
        help="Optional folder name for the output bundle (defaults to a slug of the keywords).",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=0,
        help="Include this many lines of context before/after each match in the manifest (default: 0).",
    )
    parser.add_argument(
        "--extensions",
        type=str,
        default=",".join(sorted(SUPPORTED_EXTENSIONS)),
        help="Comma-separated list of file extensions to scan (default: .md,.txt).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.regex:
        search_terms = [args.keywords[0]]
    else:
        search_terms = args.keywords

    extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.extensions.split(",") if ext}
    matches = search_and_copy(
        chapters_root=args.chapters_root,
        output_root=args.output_root,
        keywords=search_terms,
        use_regex=args.regex,
        context_lines=args.context_lines,
        extensions=extensions,
        slug=args.slug,
    )

    print(
        f"Copied {matches} file(s) containing {search_terms[0] if args.regex else search_terms} "
        f"to {(args.output_root / (args.slug or slugify('_'.join(search_terms))))}"
    )


if __name__ == "__main__":
    main()
