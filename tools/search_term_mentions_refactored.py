#!/usr/bin/env python3
import sys
import os
import re
from pathlib import Path

def search_term_mentions(term: str, context_lines: int = 2, base_dir: str = "chapters", out_dir: str = "search_results"):
	base_path = Path(base_dir)
	output_path = Path(out_dir) / term.replace(" ", "_")
	output_path.mkdir(parents=True, exist_ok=True)

	pattern = re.compile(re.escape(term), re.IGNORECASE)
	results = []

	for file_path in base_path.rglob("*.txt"):
		lines = file_path.read_text(encoding='utf-8').splitlines()
		for idx, line in enumerate(lines):
			if pattern.search(line):
				start = max(0, idx - context_lines)
				end = min(len(lines), idx + context_lines + 1)
				snippet = "\n".join(lines[start:end])
				result_path = output_path / f"match_{{file_path.stem}}_{{idx}}.txt"
				result_text = f"File: {{file_path}}\nMatch at line {{idx + 1}}:\n\n{{snippet}}"
				result_path.write_text(result_text, encoding='utf-8')
				results.append(result_path)

	print(f"Found {len(results)} matches for '{term}'. Snippets written to '{output_path}'.")


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python3 search_term_mentions.py \"search term\"")
		sys.exit(1)
	term = sys.argv[1]
	context_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 2
	search_term_mentions(term, context_lines)
