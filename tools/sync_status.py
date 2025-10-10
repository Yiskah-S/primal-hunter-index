#!/usr/bin/env python3
"""Copy the latest z_codex_context/status_*.md into docs/logs/ for historical snapshots."""

from __future__ import annotations

import shutil
from pathlib import Path

STATUS_DIR = Path("z_codex_context")
TARGET_DIR = Path("docs") / "logs"


def sync_latest_status() -> None:
	snapshots = sorted(STATUS_DIR.glob("status_*.md"))
	if not snapshots:
		print("No status snapshot found under z_codex_context/.")
		return
	latest = snapshots[-1]
	TARGET_DIR.mkdir(parents=True, exist_ok=True)
	destination = TARGET_DIR / latest.name
	shutil.copy2(latest, destination)
	print(f"📄 Copied {latest} -> {destination}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
	sync_latest_status()
