#!/usr/bin/env python3
"""MediaWiki helpers for seeding tagging vocabularies."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests

from core.io_safe import write_json_atomic

BASE_API = "https://the-primal-hunter.fandom.com/api.php"

DEFAULT_CATEGORIES_OUTPUT = Path("tagging/ph_wiki_categories.json")
DEFAULT_TAG_OUTPUT = Path("tagging/tag_candidates.json")
SLEEP = 0.2


def mw_api(params: dict) -> dict:
	"""Invoke the MediaWiki API and return a decoded JSON payload."""
	base = {"format": "json"}
	resp = requests.get(BASE_API, params={**base, **params}, timeout=30)
	resp.raise_for_status()
	data = resp.json()
	if "error" in data:
		raise RuntimeError(f"MW API error: {data['error']}")
	return data


def fetch_all_categories(limit: int = 5000) -> list[str]:
	"""Collect MediaWiki categories up to *limit* entries."""
	categories: list[str] = []
	params = {"action": "query", "list": "allcategories", "aclimit": min(limit, 500)}
	total = 0
	while True:
		data = mw_api(params)
		batch = [c["*"] for c in data.get("query", {}).get("allcategories", [])]
		categories.extend(batch)
		total += len(batch)
		cont = data.get("continue", {}).get("accontinue")
		if not cont or total >= limit:
			break
		params["accontinue"] = cont
		time.sleep(SLEEP)
	return categories[:limit]


def fetch_pages_for_category(cat_name: str, limit: int = 5000) -> list[str]:
	"""Return page titles that belong to a wiki category."""
	titles: list[str] = []
	params = {
		"action": "query",
		"list": "categorymembers",
		"cmtitle": f"Category:{cat_name}",
		"cmlimit": min(limit, 500),
		"cmtype": "page|subcat",
	}
	total = 0
	while True:
		data = mw_api(params)
		members = data.get("query", {}).get("categorymembers", [])
		for m in members:
			title = m.get("title", "")
			if not title:
				continue
			if any(title.startswith(ns + ":") for ns in ("File", "Template", "Help", "Module", "User", "Forum")):
				continue
			titles.append(title)
		total += len(members)
		cont = data.get("continue", {}).get("cmcontinue")
		if not cont or total >= limit:
			break
		params["cmcontinue"] = cont
		time.sleep(SLEEP)
	return titles[:limit]


def run_categories_mode(output: Path, limit: int = 5000) -> None:
	"""Serialize category metadata for offline review."""
	cats = fetch_all_categories(limit=limit)
	out = {
		"source": BASE_API,
		"count": len(cats),
		"categories": [
			{"name": c, "url": f"https://the-primal-hunter.fandom.com/wiki/Category:{c.replace(' ', '_')}"}
			for c in cats
		],
	}
	write_json_atomic(output, out, ensure_ascii=False, indent=2)
	print(f"✅ Saved {len(cats)} categories to: {output}")


def run_pages_mode(categories_file: Path | None, single_category: str | None, output: Path, limit: int = 5000) -> None:
	"""Collect wiki page titles for each category and write tag candidates."""
	if single_category:
		cats = [{"name": single_category}]
	else:
		if not categories_file or not categories_file.exists():
			raise FileNotFoundError("Categories file missing. Provide --categories-file or --category.")
		doc = json.loads(categories_file.read_text(encoding="utf-8"))
		cats = doc.get("categories", [])
		if cats and isinstance(cats[0], str):
			cats = [{"name": c} for c in cats]

	buckets: dict[str, list[str]] = {}
	for i, entry in enumerate(cats, 1):
		name = entry.get("name")
		if not name:
			continue
		print(f"[{i}/{len(cats)}] 🔎 Fetching members for category: {name}")
		titles = fetch_pages_for_category(name, limit=limit)
		buckets[name] = titles
		time.sleep(SLEEP)

	write_json_atomic(output, buckets, ensure_ascii=False, indent=2)
	print(f"✅ Wrote tag candidates for {len(buckets)} categories to: {output}")


def main():
	parser = argparse.ArgumentParser(description="Extract tag target vocab from the Primal Hunter Fandom wiki")
	sub = parser.add_subparsers(dest="mode", required=True)

	p_cat = sub.add_parser("categories", help="Fetch all wiki categories via API")
	p_cat.add_argument("--output", type=Path, default=DEFAULT_CATEGORIES_OUTPUT)
	p_cat.add_argument("--limit", type=int, default=5000, help="Max categories to fetch")

	p_pages = sub.add_parser("pages", help="Fetch page titles for categories via API")
	p_pages.add_argument(
		"--categories-file",
		type=Path,
		default=DEFAULT_CATEGORIES_OUTPUT,
		help="Path to JSON file produced by 'categories' mode",
	)
	p_pages.add_argument("--category", type=str, help="Fetch a single category by name (e.g., 'Skills')")
	p_pages.add_argument("--output", type=Path, default=DEFAULT_TAG_OUTPUT)
	p_pages.add_argument("--limit", type=int, default=5000, help="Max pages per category")

	args = parser.parse_args()

	if args.mode == "categories":
		run_categories_mode(args.output, limit=args.limit)
	elif args.mode == "pages":
		run_pages_mode(args.categories_file, args.category, args.output, limit=args.limit)


if __name__ == "__main__":
	main()
