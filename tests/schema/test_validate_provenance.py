# tests/schema/test_validate_provenance.py
import subprocess
from pathlib import Path


def test_validate_provenance_exits_zero(repo_root: Path = Path(__file__).resolve().parents[2]):
	tool = repo_root / "tools" / "validate_provenance.py"
	res = subprocess.run(["python3", str(tool), "--allow-inline"], cwd=repo_root)
	assert res.returncode in (0,), "Provenance violations exist; fix guardrails or test fixtures."
