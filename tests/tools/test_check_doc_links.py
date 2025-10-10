from pathlib import Path

from tools.check_doc_links import collect_broken_links


def test_collect_broken_links_identifies_missing_targets(tmp_path: Path) -> None:
	docs_root = tmp_path / "docs"
	docs_root.mkdir(parents=True)
	# valid target
	(docs_root / "existing.md").write_text("# ok\n", encoding="utf-8")
	(docs_root / "main.md").write_text(
		"[Good](existing.md)\n[Missing](absent.md)\n", encoding="utf-8"
	)
	errors = collect_broken_links(docs_root)
	assert errors and "Missing" in errors[0]


def test_collect_broken_links_clean(tmp_path: Path) -> None:
	docs_root = tmp_path / "docs"
	docs_root.mkdir(parents=True)
	(docs_root / "existing.md").write_text("# ok\n", encoding="utf-8")
	(docs_root / "main.md").write_text("[Good](existing.md)\n", encoding="utf-8")
	assert collect_broken_links(docs_root) == []
