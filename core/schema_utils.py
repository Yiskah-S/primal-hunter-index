import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import validate, Draft202012Validator

def read_json(path: str) -> Any:
	path = Path(path)
	return json.loads(path.read_text()) if path.exists() else {}

def write_json_atomic(path: str, data: Any) -> None:
	p = Path(path)
	tmp = p.with_suffix(p.suffix + ".tmp")
	tmp.write_text(json.dumps(data, indent=2))
	tmp.replace(p)

def load_schema(path: str) -> Dict[str, Any]:
	return read_json(path)

def validate_instance(instance: Any, schema: Dict[str, Any]) -> None:
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
	if errors:
		msg = "\n".join(f"- {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors)
		raise ValueError(f"Schema validation failed:\n{msg}")
