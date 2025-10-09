#!/usr/bin/env python3
"""
Create a .meta.json sidecar file for a records JSON file.
Ensures provenance is recorded and validation tooling can run cleanly.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from core.io_safe import write_json_atomic


def main():
    parser = argparse.ArgumentParser(description="Create a metadata sidecar for a records JSON file.")
    parser.add_argument("target", type=Path, help="Path to the core JSON file (e.g. records/skills.json)")
    parser.add_argument("--entered-by", type=str, choices=["human", "assistant"], required=True,
                        help="Who is entering this file? Must be 'human' or 'assistant'")
    parser.add_argument("--book", type=str, help="Book name or number (optional)")
    parser.add_argument("--chapter", type=int, help="Chapter number (optional)")
    parser.add_argument("--scene", type=int, help="Scene number in this chapter")
    parser.add_argument("--scene-id", type=str, help="Scene ID string (e.g. '01-02-01')")
    parser.add_argument("--line", type=int, help="Line number in the source file (optional)")
    parser.add_argument("--notes", type=str, help="Optional freeform notes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing sidecar if it exists")

    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists():
        print(f"❌ File not found: {target}")
        sys.exit(1)

    if target.suffix != ".json":
        print(f"❌ Target must be a .json file, got: {target.name}")
        sys.exit(1)

    sidecar_path = target.with_suffix(target.suffix + ".meta.json")
    if sidecar_path.exists() and not args.force:
        print(f"⚠️ Sidecar already exists: {sidecar_path} (use --force to overwrite)")
        sys.exit(1)

    sidecar_data = {
        "records": False,
        "entered_by": args.entered_by,
        "reviewed_by_human": False,
        "last_updated": str(date.today()),
        "source": {
            "book": args.book,
            "chapter": args.chapter,
            "scene": args.scene,
            "scene_id": args.scene_id,
            "line": args.line
        }
    }

    if args.notes:
        sidecar_data["notes"] = args.notes

    write_json_atomic(sidecar_path, sidecar_data, ensure_ascii=False)
    print(f"✅ Sidecar created: {sidecar_path}")

if __name__ == "__main__":
    main()
