#!/usr/bin/env python3
"""Estimate token counts for chapter files using tiktoken.

Examples
--------
python3 tools/token_estimator.py \
    --chapters-root chapters \
    --model gpt-4o-mini \
    --extensions .md .txt \
    --per-file
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

try:
    import tiktoken
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None  # type: ignore


def iter_text_files(root: Path, extensions: Iterable[str]) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in extensions]


def resolve_encoding(model: str):
    if tiktoken is None:
        raise RuntimeError(
            "tiktoken is not installed. Install it with 'pip install tiktoken' before running this script."
        )

    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Fall back to a general-purpose encoding if the model is unknown.
        return tiktoken.get_encoding("cl100k_base")


def estimate_tokens(file_paths: Iterable[Path], encoding, chapters_root: Path, per_file: bool) -> int:
    total_tokens = 0

    for file_path in file_paths:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        token_count = len(encoding.encode(text))
        total_tokens += token_count
        if per_file:
            print(f"{file_path.relative_to(chapters_root)}: {token_count:,} tokens")

    return total_tokens


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate tokens for chapter files using tiktoken.")
    parser.add_argument(
        "--chapters-root",
        type=Path,
        default=Path("chapters"),
        help="Directory containing chapter files (default: chapters/).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="Model name to use for token encoding (default: gpt-4).",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[".md"],
        help="File extensions (including dot) to include (default: .md).",
    )
    parser.add_argument(
        "--per-file",
        action="store_true",
        help="Print the token count for each file individually.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.extensions}

    if not args.chapters_root.exists():
        print(f"❌ Chapters root '{args.chapters_root}' does not exist.")
        sys.exit(1)

    file_paths = iter_text_files(args.chapters_root, extensions)
    if not file_paths:
        print(f"⚠️ No files with extensions {sorted(extensions)} found under {args.chapters_root}.")
        sys.exit(0)

    try:
        encoding = resolve_encoding(args.model)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    total = estimate_tokens(file_paths, encoding, args.chapters_root, args.per_file)

    file_count = len(file_paths)
    file_label = "file" if file_count == 1 else "files"
    print(f"📄 Scanned {file_count} {file_label} under {args.chapters_root}")
    print(f"🔢 Approximate total tokens ({args.model}): {total:,}")


if __name__ == "__main__":
    main()
