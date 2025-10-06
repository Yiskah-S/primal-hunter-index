# tests/schema/test_promote_tags.py
import subprocess
from pathlib import Path


def test_promote_tags_dry_run(repo_root: Path = Path(__file__).resolve().parents[2]):
	res = subprocess.run(
		["python3", "-m", "tools.promote_tags", "--all"],
		cwd=repo_root,
		capture_output=True,
		text=True,
	)
	assert "Dry-run" in res.stdout
	assert res.returncode == 0
