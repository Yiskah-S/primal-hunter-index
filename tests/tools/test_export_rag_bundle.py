from pathlib import Path

from tools.export_rag_bundle import BUNDLE_FILENAMES, main as export_main


def test_export_rag_bundle_generates_outputs(tmp_path: Path) -> None:
	output_dir = tmp_path / "bundles"
	exit_code = export_main(["--output-dir", str(output_dir)])
	assert exit_code == 0
	for filename in BUNDLE_FILENAMES.values():
		path = output_dir / filename
		assert path.exists()
		lines = path.read_text(encoding="utf-8").strip().splitlines()
		assert lines and all(line.strip() for line in lines)
