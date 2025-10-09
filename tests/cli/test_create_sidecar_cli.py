import json
import subprocess
import sys
from pathlib import Path


def test_create_sidecar_cli(tmp_path):
    target = tmp_path / "record.json"
    target.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

    cmd = [
        sys.executable,
        "-m",
        "tools.create_sidecar",
        str(target),
        "--entered-by",
        "assistant",
        "--scene-id",
        "01-02-01",
    ]
    subprocess.check_call(cmd, cwd=Path.cwd())

    sidecar = json.loads(target.with_suffix(".json.meta.json").read_text(encoding="utf-8"))

    assert sidecar["entered_by"] == "assistant"
    assert sidecar["source"]["scene_id"] == "01-02-01"
    assert sidecar["records"] is False
