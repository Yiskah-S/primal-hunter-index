#!/usr/bin/env python3
"""Ensure tag usage aligns with the registry rules."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = REPO_ROOT / "records"
TAG_REGISTRY_PATH = REPO_ROOT / "tagging" / "tag_registry.json"
SKIP_FILE_SUFFIXES = (".meta.json", ".review.json", ".provenance.json")

if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))

from core.schema_utils import read_json

CATEGORY_LIMITS = {
    "narrative_style": 3,
    "character_tone": 2,
    "scene_function": 2,
}


def _iter_record_files(records_root: Path) -> Iterator[Path]:
    for path in sorted(records_root.rglob("*.json")):
        if any(path.name.endswith(suffix) for suffix in SKIP_FILE_SUFFIXES):
            continue
        yield path


def _collect_tag_strings(data: Any) -> list[tuple[str, str]]:
    collected: list[tuple[str, str]] = []

    def _walk(node: Any, pointer: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                child_pointer = f"{pointer}.{key}" if pointer else key
                if key == "tags" and isinstance(value, list):
                    for idx, item in enumerate(value):
                        collected.append((f"{child_pointer}[{idx}]", item))
                else:
                    _walk(value, child_pointer)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                child_pointer = f"{pointer}[{idx}]" if pointer else f"[{idx}]"
                _walk(item, child_pointer)

    _walk(data)
    return collected


def _load_registry(path: Path) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    raw = read_json(path)
    if not isinstance(raw, dict):
        return registry

    entries: list[dict[str, Any]] = []
    tags_value = raw.get("tags")
    if isinstance(tags_value, list):
        entries.extend([entry for entry in tags_value if isinstance(entry, dict)])
    else:
        for value in raw.values():
            if isinstance(value, list):
                entries.extend([entry for entry in value if isinstance(entry, dict)])

    def register(key: Any, entry: dict[str, Any]) -> None:
        if isinstance(key, str) and key:
            registry.setdefault(key, entry)

    for entry in entries:
        register(entry.get("id"), entry)
        register(entry.get("tag_id"), entry)
        register(entry.get("tag"), entry)
        register(entry.get("label"), entry)
        for alias in entry.get("aliases", []) or []:
            register(alias, entry)
        category = entry.get("category")
        identifier = entry.get("id") or entry.get("tag") or entry.get("tag_id")
        if isinstance(category, str) and isinstance(identifier, str) and not identifier.startswith("tag."):
            register(f"tag.{category}.{identifier}", entry)
    return registry


def validate_tags(
    records_root: Path,
    registry_path: Path,
    mode: str = "draft",
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    registry_lookup = _load_registry(registry_path)
    if not registry_lookup:
        errors.append(f"{registry_path}: tag registry is empty or invalid.")
        return errors, warnings

    for record_file in _iter_record_files(records_root):
        data = read_json(record_file)
        if data is None:
            continue
        counts: Counter[str] = Counter()
        collected = _collect_tag_strings(data)
        for pointer, raw_value in collected:
            if not isinstance(raw_value, str):
                errors.append(f"{record_file}: {pointer} contains non-string tag value {raw_value!r}")
                continue
            tag_value = raw_value.strip()
            if not tag_value:
                errors.append(f"{record_file}: {pointer} contains empty tag string")
                continue

            reg_entry = registry_lookup.get(tag_value)
            if reg_entry is None and tag_value.startswith("tag."):
                reg_entry = registry_lookup.get(tag_value.split(".", 1)[-1])
            if reg_entry is None:
                errors.append(f"{record_file}: {pointer} references unknown tag '{tag_value}'")
                continue

            status = reg_entry.get("status")
            if status == "candidate":
                message = f"{record_file}: {pointer} references candidate tag '{reg_entry.get('id', tag_value)}'"
                if mode == "export":
                    errors.append(message)
                else:
                    warnings.append(message)
            elif mode == "export" and status != "approved":
                errors.append(f"{record_file}: {pointer} references non-approved tag '{reg_entry.get('id', tag_value)}'")

            category = reg_entry.get("category")
            if isinstance(category, str):
                counts[category] += 1
                limit = CATEGORY_LIMITS.get(category)
                if limit is not None and counts[category] > limit:
                    errors.append(
                        f"{record_file}: {category} tag limit exceeded ({counts[category]} > {limit})"
                    )

    return errors, warnings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate tag usage against the registry.")
    parser.add_argument(
        "--records-root",
        type=Path,
        default=RECORDS_ROOT,
        help="Root directory containing records data (default: %(default)s)",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=TAG_REGISTRY_PATH,
        help="Path to tag_registry.json (default: %(default)s)",
    )
    parser.add_argument(
        "--mode",
        choices=["draft", "export"],
        default="draft",
        help="Draft mode downgrades candidate tags to warnings; export mode fails on them.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors, warnings = validate_tags(args.records_root, args.registry, mode=args.mode)
    for warning in warnings:
        print(f"⚠️  {warning}")
    for error in errors:
        print(f"❌ {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
