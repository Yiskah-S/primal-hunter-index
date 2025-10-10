#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import pathlib
import re
import zipfile
from datetime import datetime

TAB_VIOLATION_RE = re.compile(r"^\t+ +| +\t+")


def find_tab_violations(file_path):
	bad_lines = []
	try:
		with open(file_path, encoding="utf-8") as f:
			for i, line in enumerate(f, 1):
				if TAB_VIOLATION_RE.search(line):
					bad_lines.append(i)
	except Exception:
		pass
	return bad_lines


def glob_many(root, patterns):
	matches = set()
	for pat in patterns:
		for path, _, files in os.walk(root):
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


def filter_out(paths, excludes):
	return [p for p in paths if not any(fnmatch.fnmatch(p, ex) for ex in excludes)]


def validate_tabs(repo_path, paths):
	violations = {}
	for rel_path in paths:
		full_path = repo_path / rel_path
		if full_path.suffix in [".py", ".json"]:
			bad_lines = find_tab_violations(full_path)
			if bad_lines:
				violations[rel_path] = bad_lines
	return violations


def bundle_files(repo_path, files, output_path, verbose=False):
	with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
		for rel_path in files:
			if verbose:
				print(f"➕ {rel_path}")
			zipf.write(repo_path / rel_path, rel_path)


def main():
	parser = argparse.ArgumentParser(description="Make a bundle for upload")
	parser.add_argument("--dry-run", action="store_true", help="List files that would be bundled")
	parser.add_argument("--force", action="store_true", help="Skip tab/space compliance check")
	parser.add_argument("--verbose", "-v", action="store_true", help="Print each file added to the bundle")
	args = parser.parse_args()

	repo = pathlib.Path(__file__).resolve().parents[1]
	manifest = repo / "__sandbox__" / "project_upload_manifest.json"
	if not manifest.exists():
		raise FileNotFoundError("Manifest missing: __sandbox__/project_upload_manifest.json")

	cfg = json.loads(manifest.read_text())
	include = cfg.get("include", [])
	exclude = cfg.get("exclude", [])
	bundle_name = cfg.get("bundle_name", "phi_upload_bundle")

	all_included = glob_many(str(repo), include)
	final_files = filter_out(all_included, exclude)

	if not final_files:
		print("⚠️  No files matched. Check your manifest patterns.")
		return

	# Tab validation
	if not args.force:
		violations = validate_tabs(repo, final_files)
		if violations:
			print("❌ Tab/space violations found:")
			for path, lines in violations.items():
				print(f" - {path}: lines {lines}")
			print("\n💡 Fix issues or rerun with --force to override.")
			return

	# Dry run?
	if args.dry_run:
		print("📦 DRY RUN — These files would be included:")
		for f in final_files:
			print(f" - {f}")
		return

	# Output bundle
	timestamp = datetime.now().strftime("%Y%m%d_%H%M")
	bundle_dir = repo.parent / "z_notes" / "project_zips"
	bundle_dir.mkdir(parents=True, exist_ok=True)
	zip_path = bundle_dir / f"{bundle_name}_{timestamp}.zip"

	bundle_files(repo, final_files, zip_path, verbose=args.verbose)

	print(f"✅ Bundle created: {zip_path}")


if __name__ == "__main__":
	main()
