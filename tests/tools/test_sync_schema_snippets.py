import json
from pathlib import Path

from tools.sync_schema_snippets import sync_document


def test_sync_document_updates_mismatched_snippet(tmp_path: Path) -> None:
	schema_path = tmp_path / "schemas" / "example.schema.json"
	schema_path.parent.mkdir(parents=True, exist_ok=True)
	schema = {"title": "Example", "type": "object"}
	schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

	doc_path = tmp_path / "docs" / "contract.md"
	doc_path.parent.mkdir(parents=True, exist_ok=True)
	doc_path.write_text(
		'## Spec\n\n*(Drop into `schemas/example.schema.json`)*\n\n```json\n{"out_of_sync": true}\n```\n',
		encoding="utf-8",
	)

	changed = sync_document(doc_path, check=False, repo_root=tmp_path)
	assert changed
	expected = json.dumps(schema, indent=2)
	assert expected in doc_path.read_text(encoding="utf-8")


def test_sync_document_check_detects_drift(tmp_path: Path) -> None:
	schema_path = tmp_path / "schemas" / "example.schema.json"
	schema_path.parent.mkdir(parents=True, exist_ok=True)
	schema_path.write_text(json.dumps({"const": 1}, indent=2), encoding="utf-8")
	doc_path = tmp_path / "docs" / "contract.md"
	doc_path.parent.mkdir(parents=True, exist_ok=True)
	doc_path.write_text("*(Drop into `schemas/example.schema.json`)*\n\n```json\n{}\n```\n", encoding="utf-8")
	assert sync_document(doc_path, check=True, repo_root=tmp_path)
