# tools/promote_tags.py
#!/usr/bin/env python3
r"""
Promote tag candidates into the approved tag registry.

Usage:
  python -m tools.promote_tags --all --commit
  python -m tools.promote_tags --ids skill.meditation,entity.jake
  python -m tools.promote_tags --grep "skill\."

Notes:
- Validates output against schemas/tag_registry.schema.json.
- Writes atomically via core.io_safe.write_json_atomic.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from core.io_safe import write_json_atomic  # tabs > spaces, keep your style
from core.schema_utils import validate_json_file  # assumes you have a helper

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = REPO_ROOT / "tagging" / "tag_candidates.json"
REGISTRY = REPO_ROOT / "tagging" / "tag_registry.json"
SCHEMA = REPO_ROOT / "schemas" / "tag_registry.schema.json"


def load_json(path: Path) -> dict:
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Promote tag candidates into registry.")
	grp = p.add_mutually_exclusive_group(required=True)
	grp.add_argument("--all", action="store_true", help="Promote all candidates.")
	grp.add_argument("--ids", type=str, help="Comma-separated list of candidate IDs to promote.")
	grp.add_argument("--grep", type=str, help="Promote candidates whose ID matches this regex.")
	p.add_argument("--commit", action="store_true", help="Write changes (otherwise dry-run).")
	p.add_argument("--backup", action="store_true", help="Write .bak timestamped file alongside commits.")
	return p.parse_args()


def select_ids(candidates: dict, args: argparse.Namespace) -> list[str]:
	ids = list(candidates.keys())
	if args.all:
		return ids
	if args.ids:
		want = [s.strip() for s in args.ids.split(",") if s.strip()]
		missing = [w for w in want if w not in candidates]
		if missing:
			raise SystemExit(f"IDs not found in candidates: {missing}")
		return want
	if args.grep:
		reg = re.compile(args.grep)
		return [i for i in ids if reg.search(i)]
	raise AssertionError("one of --all/--ids/--grep must be provided")


def merge_into_registry(registry: dict, candidates: dict, chosen: list[str]) -> tuple[dict, list[str]]:
	added = []
	for tid in chosen:
		if tid in registry:
			# Idempotent: skip if identical; replace if different
			if registry[tid] != candidates[tid]:
				registry[tid] = candidates[tid]
				added.append(tid)
		else:
			registry[tid] = candidates[tid]
			added.append(tid)
	return registry, added


def main() -> None:
	args = parse_args()
	cands = load_json(CANDIDATES)
	reg = load_json(REGISTRY)
	chosen = select_ids(cands, args)

	new_reg, changed = merge_into_registry(reg, cands, chosen)
	if not changed:
		print("No changes (already present / identical).")
		return

	# Validate against schema before writing
	validate_json_file(new_reg, SCHEMA)

	if args.commit:
		write_json_atomic(REGISTRY, new_reg, make_backup=args.backup)
		print(f"Committed {len(changed)} tags → {REGISTRY}")
	else:
		print(f"Dry-run: would add/replace {len(changed)} tags:")
		for tid in changed:
			print(f"  - {tid}")


if __name__ == "__main__":
	main()
