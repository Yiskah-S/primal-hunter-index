#!/usr/bin/env python3
"""Validate provenance guardrails across the repository.

This script enforces the contract expectations from
`docs/contracts/provenance_contract_v2.0.md` by checking that:

* Character timelines include a non-empty `source_ref[]` for every entry.
* Citations contain the required fields when `type = scene`.
* Low-certainty and inferred citations surface as warnings.
* Canonical record payloads do not embed inline `source_ref` blocks.

The validator prints human-readable error messages and exits with status 1
if any hard violations are found.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.schema_utils import read_json

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))

RECORDS_DIR = Path("records")
CHARACTERS_DIR = RECORDS_DIR / "characters"
ALLOWED_INLINE_FILENAMES = {"timeline.json"}
SOURCE_REF_ALLOWED_ROOTS = {
	RECORDS_DIR / "characters",
	Path("tagging"),
}
SCENE_ID_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{2}$")


@dataclass
class Finding:
	path: Path
	message: str

	def render(self, prefix: str) -> str:
		return f"{prefix}: {self.path}: {self.message}"


def _iter_timeline_files() -> Iterator[Path]:
	if not CHARACTERS_DIR.exists():
		return
	for character_dir in CHARACTERS_DIR.iterdir():
		if not character_dir.is_dir():
			continue
		timeline_path = character_dir / "timeline.json"
		if timeline_path.exists():
			yield timeline_path


def _normalize_path(path: Path) -> Path:
	try:
		return path.relative_to(Path.cwd())
	except ValueError:
		return path


def _is_relative_to(path: Path, other: Path) -> bool:
	try:
		path.relative_to(other)
		return True
	except ValueError:
		return False

def _check_source_ref_fields(ref: dict[str, Any], ref_prefix: str, path: Path, errors: list[Finding],
							warnings: list[Finding]) -> tuple[list[Finding], list[Finding]]:
    """Validate individual source_ref object."""
    scene_id = ref.get("scene_id")
    line_start = ref.get("line_start")
    line_end = ref.get("line_end")

    if not isinstance(ref, dict):
        errors.append(Finding(_normalize_path(path), f"{ref_prefix} must be an object"))
        return errors, warnings

    ref_type = ref.get("type")
    if ref_type != "scene":
        # Soft rule: if inferred, must have inference_note
        if ref_type == "inferred" and not ref.get("inference_note"):
            warnings.append(Finding(_normalize_path(path), f"{ref_prefix} inferred but missing inference_note"))
        return errors, warnings

    # Hard validation for scene refs
    if not isinstance(scene_id, str) or not SCENE_ID_PATTERN.match(scene_id):
        errors.append(Finding(_normalize_path(path), f"{ref_prefix}.scene_id '{scene_id}' must match BB-CC-SS"))
    if not isinstance(line_start, int) or not isinstance(line_end, int):
        errors.append(Finding(_normalize_path(path), f"{ref_prefix}.line_start and line_end must be ints"))
    elif line_start > line_end:
        errors.append(
            Finding(
                _normalize_path(path),
                f"{ref_prefix}.line_start ({line_start}) cannot exceed line_end ({line_end})"
            )
        )

    # Soft guidance: review low certainty
    if ref.get("certainty") == "low":
        warnings.append(Finding(_normalize_path(path), f"{ref_prefix} marked certainty=low; ensure manual review"))

    return errors, warnings

def _validate_timeline_file(path: Path) -> tuple[list[Finding], list[Finding]]:
    """Validate a character timeline file structure and source_ref compliance."""
    data = read_json(path)
    errors, warnings = [], []

    if not isinstance(data, list):
        errors.append(Finding(_normalize_path(path), "timeline must be a JSON array of events"))
        return errors, warnings

    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            errors.append(Finding(_normalize_path(path), f"event[{index}] must be an object"))
            continue

        entry_prefix = f"event[{index}]"
        ev_errors, ev_warnings = _check_event_source_refs(entry, entry_prefix, path)
        errors.extend(ev_errors)
        warnings.extend(ev_warnings)

    return errors, warnings


def _check_event_source_refs(
    entry: dict[str, Any],
    entry_prefix: str,
    path: Path
) -> tuple[list[Finding], list[Finding]]:
    """Validate all source_ref[] entries for a single event."""
    errors, warnings = [], []
    source_refs = entry.get("source_ref")

    # Hard fail: must be non-empty list
    if not isinstance(source_refs, list) or not source_refs:
        errors.append(Finding(_normalize_path(path), f"{entry_prefix} missing non-empty source_ref[]"))
        return errors, warnings

    for i, ref in enumerate(source_refs):
        ref_prefix = f"{entry_prefix}.source_ref[{i}]"
        errors, warnings = _check_source_ref_fields(ref, ref_prefix, path, errors, warnings)

    # Soft guidance: if none have quotes or inference flags
    has_quote = any(isinstance(r, dict) and "quote" in r for r in source_refs)
    has_inference = any(isinstance(r, dict) and r.get("inference") for r in source_refs)
    if not (has_quote or has_inference):
        warnings.append(Finding(_normalize_path(path), f"{entry_prefix} has no quotes or inference hints"))

    return errors, warnings


def _iter_canonical_files() -> Iterable[Path]:
	for json_path in RECORDS_DIR.rglob("*.json"):
		name = json_path.name
		if name.endswith((".meta.json", ".review.json", ".provenance.json")):
			continue
		if name in ALLOWED_INLINE_FILENAMES:
			continue
		if any(_is_relative_to(json_path, root) for root in SOURCE_REF_ALLOWED_ROOTS):
			continue
		yield json_path


def _discover_inline_source_refs(path: Path) -> list[str]:
	data = read_json(path)
	stack: list[tuple[Any, str]] = [(data, "<root>")]
	citations: list[str] = []

	while stack:
		node, location = stack.pop()
		if isinstance(node, dict):
			for key, value in node.items():
				next_location = f"{location}.{key}" if location != "<root>" else key
				if key == "source_ref":
					citations.append(next_location)
				stack.append((value, next_location))
		elif isinstance(node, list):
			for idx, item in enumerate(node):
				stack.append((item, f"{location}[{idx}]"))
	return citations


def _validate_inline_source_refs() -> list[Finding]:
	findings: list[Finding] = []
	for path in _iter_canonical_files():
		citations = _discover_inline_source_refs(path)
		if citations:
			for location in citations:
				findings.append(
					Finding(
						_normalize_path(path),
						f"inline source_ref found at {location}; move to sidecar or timeline",
					)
				)
	return findings


def parse_args(argv: list[str]) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Validate provenance guardrails.")
	parser.add_argument(
		"--allow-inline",
		action="store_true",
		help="Downgrade inline source_ref findings to warnings (temporary migration aid).",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	ns = parse_args(argv or sys.argv[1:])
	errors: list[Finding] = []
	warnings: list[Finding] = []

	for timeline_path in _iter_timeline_files():
		timeline_errors, timeline_warnings = _validate_timeline_file(timeline_path)
		errors.extend(timeline_errors)
		warnings.extend(timeline_warnings)

	inline_findings = _validate_inline_source_refs()
	if ns.allow_inline:
		warnings.extend(inline_findings)
	else:
		errors.extend(inline_findings)

	for warning in warnings:
		print(warning.render("WARN"), file=sys.stderr)

	if errors:
		for error in errors:
			print(error.render("ERROR"), file=sys.stderr)
		return 1

	if warnings:
		print("Provenance validation passed with warnings.", file=sys.stdout)
	else:
		print("Provenance validation passed.", file=sys.stdout)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
