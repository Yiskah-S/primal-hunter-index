import json
from pathlib import Path

from tools.validate_ids import collect_event_id_findings


def write_json(path: Path, payload) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_collect_event_id_findings_strict_failure(tmp_path: Path) -> None:
	records_root = tmp_path / "records"
	timeline = [
		{"event_id": "ev.hero.01.01.01.invalid slug"},
		{"event_id": "ev.hero.01.01.01.duplicate"},
		{"event_id": "ev.hero.01.01.01.duplicate"},
	]
	write_json(records_root / "characters" / "hero" / "timeline.json", timeline)
	errors, warnings = collect_event_id_findings(records_root, strict=True)
	assert errors  # invalid pattern + duplicate
	assert not warnings


def test_collect_event_id_findings_non_strict(tmp_path: Path) -> None:
	records_root = tmp_path / "records"
	timeline = [
		{"scene_id": "01.01.01"},  # missing event_id triggers warning only
		{"event_id": "ev.hero.01.01.01.valid_entry"},
	]
	write_json(records_root / "characters" / "hero" / "timeline.json", timeline)
	errors, warnings = collect_event_id_findings(records_root, strict=False)
	assert not errors
	assert warnings
	errors_strict, warnings_strict = collect_event_id_findings(records_root, strict=True)
	assert errors_strict  # strict mode upgrades missing ID to error
