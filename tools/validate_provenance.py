# tools/validate_provenance.py
#!/usr/bin/env python3
"""
Provenance validator — enforces guardrails from provenance_contract.md.

Rules:
  1) Timeline events MUST have source_ref[] with scene_id + line range.
  2) Warn if timeline event has no 'quote' nor 'inference' flag (soft guidance).
  3) Canon payloads in records/** (non-timeline) MUST NOT include inline source_ref[].
     Exception: *.meta.json sidecars (file-level provenance) are allowed.
  4) .meta.json must carry a well-formed record_log[] if present.
  5) scene_id strings must match ^\\d{2}-\\d{2}-\\d{2}$.

Exit codes: 0 = ok, 1 = violations.
"""
from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDS = REPO_ROOT / "records"
SCENE_ID_RE = re.compile(r"^\d{2}-\d{2}-\d{2}$")

Violation = tuple[str, Path, str]  # (level, path, message)


def load_json(p: Path) -> dict | list:
	with p.open("r", encoding="utf-8") as f:
		return json.load(f)


def iter_json_files(root: Path) -> Iterator[Path]:
    yield from sorted(root.rglob("*.json"))

def is_timeline_file(p: Path) -> bool:
	return "timeline" in p.stem or p.name == "timeline.json"


def is_meta_sidecar(p: Path) -> bool:
	return p.name.endswith(".meta.json")


def check_scene_id(scene_id: str) -> bool:
	return bool(SCENE_ID_RE.match(scene_id))


def check_timeline_file(path: Path, payload) -> list[Violation]:
	violations: list[Violation] = []
	if not isinstance(payload, list):
		violations.append(("fail", path, "timeline should be a JSON array of events"))
		return violations

	for idx, ev in enumerate(payload):
		loc = f"event[{idx}]"
		sr = ev.get("source_ref")
		if not isinstance(sr, list) or not sr:
			violations.append(("fail", path, f"{loc}: missing source_ref[]"))
			continue
		for j, ref in enumerate(sr):
			rpath = f"{loc}.source_ref[{j}]"
			sid = ref.get("scene_id")
			if not isinstance(sid, str) or not check_scene_id(sid):
				violations.append(("fail", path, f"{rpath}: invalid scene_id '{sid}'"))
			for key in ("line_start", "line_end"):
				if not isinstance(ref.get(key), int):
					violations.append(("fail", path, f"{rpath}: {key} must be int"))

		# Soft guidance: warn if neither quote nor inference flags exist
		has_quote = any("quote" in r for r in sr)
		has_inference = bool(ev.get("inference")) or any(r.get("inference") for r in sr if isinstance(r, dict))
		if not (has_quote or has_inference):
			violations.append(("warn", path, f"{loc}: no quotes or inference hints provided"))
	return violations


def scan_for_inline_source_ref(path: Path, payload) -> list[Violation]:
	"""
	Walk any dict/list payload and report if 'source_ref' appears where it shouldn't.
	Allowed: timelines (handled separately) and *.meta.json.
	"""
	violations: list[Violation] = []

	def _walk(node, trail: str = "$"):
		if isinstance(node, dict):
			if "source_ref" in node:
				violations.append(("fail", path, f"inline source_ref found at {trail}"))
			for k, v in node.items():
				_walk(v, f"{trail}.{k}")
		elif isinstance(node, list):
			for i, v in enumerate(node):
				_walk(v, f"{trail}[{i}]")

	_walk(payload)
	return violations


def check_meta_sidecar(path: Path, payload) -> list[Violation]:
	violations: list[Violation] = []
	# record_log[] is optional but if present must be an array of objects with minimal fields
	log = payload.get("record_log")
	if log is None:
		return violations
	if not isinstance(log, list):
		violations.append(("fail", path, "record_log must be an array"))
		return violations
	for i, entry in enumerate(log):
		if not isinstance(entry, dict):
			violations.append(("fail", path, f"record_log[{i}] must be an object"))
			continue
		if "timestamp" not in entry or "action" not in entry:
			violations.append(("fail", path, f"record_log[{i}] missing 'timestamp' or 'action'"))
	return violations


def main() -> int:
	violations: list[Violation] = []
	for p in iter_json_files(RECORDS):
		payload = load_json(p)
		if is_timeline_file(p) and not is_meta_sidecar(p):
			violations.extend(check_timeline_file(p, payload))
			continue
		if is_meta_sidecar(p):
			violations.extend(check_meta_sidecar(p, payload))
			continue
		# Regular canon files: must NOT contain inline source_ref anywhere
		violations.extend(scan_for_inline_source_ref(p, payload))

	# Print and choose exit code
	has_fail = False
	for level, path, msg in violations:
		prefix = "FAIL" if level == "fail" else "WARN"
		if level == "fail":
			has_fail = True
		print(f"[{prefix}] {path.relative_to(REPO_ROOT)} :: {msg}")

	return 1 if has_fail else 0


if __name__ == "__main__":
	sys.exit(main())
