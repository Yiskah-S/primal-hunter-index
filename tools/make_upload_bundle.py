#!/usr/bin/env python3
import fnmatch
import json
import os
import pathlib
import time
import zipfile


def _glob_many(root, patterns):
    matches = set()
    for pat in patterns:
        for path, dirs, files in os.walk(root):
            rel = os.path.relpath(path, root)
            for f in files:
                p = os.path.join(rel, f) if rel != "." else f
                if fnmatch.fnmatch(p, pat):
                    matches.add(p)
            if fnmatch.fnmatch(rel, pat):
                for f in files:
                    p = os.path.join(rel, f) if rel != "." else f
                    matches.add(p)
    return sorted(matches)


def _filter_out(paths, excludes):
    out = []
    for p in paths:
        skip = any(fnmatch.fnmatch(p, ex) for ex in excludes)
        if not skip:
            out.append(p)
    return out


def main():
    repo = pathlib.Path(__file__).resolve().parents[1]
    manifest = repo / "__sandbox__" / "project_upload_manifest.json"

    print("Repo path:", repo)
    print("Looking for manifest at:", manifest)

    if not manifest.exists():
        raise SystemExit("__sandbox__ not found at repo root or file project_upload_manifest.json not found")

    cfg = json.loads(manifest.read_text())
    include = cfg.get("include", [])
    exclude = cfg.get("exclude", [])
    name = cfg.get("bundle_name", "phi_upload_bundle")

    all_included = _glob_many(str(repo), include)
    final_files = _filter_out(all_included, exclude)
    if not final_files:
        raise SystemExit("No files selected; check manifest include/exclude patterns.")

    dist = repo / "/Users/jessica/Projects/z_notes/project_zips"
    dist.mkdir(exist_ok=True)
    tstamp = time.strftime("%Y%m%d_%H%M%S")
    out_zip = dist / f"{name}_{tstamp}.zip"

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in final_files:
            abs_path = repo / rel
            if not abs_path.exists():
                continue
            z.write(
                abs_path,
                arcname=rel,
            )

    print(f"✅ Created: {out_zip}")


if __name__ == "__main__":
    import sys

    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
