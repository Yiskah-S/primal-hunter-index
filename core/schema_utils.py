import json
from pathlib import Path
from typing import Any, Dict
from jsonschema import Draft202012Validator, ValidationError

def read_json(path: str | Path) -> Any:
	path = Path(path)
	return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def write_json_atomic(path: str | Path, data: Any) -> None:
	p = Path(path)
	tmp = p.with_suffix(p.suffix + ".tmp")
	tmp.write_text(json.dumps(data, indent=2))
	tmp.replace(p)

def load_schema(path: str | Path) -> Dict[str, Any]:
	return read_json(path)

def validate_instance(instance: Any, schema: Dict[str, Any]) -> None:
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
	if errors:
		msg = "\n".join(f"- {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors)
		raise ValueError(f"Schema validation failed:\n{msg}")

def validate_json_schema(data_path: Path, schema_path: Path, name: str = None) -> None:
	try:
		data = read_json(data_path)
		schema = load_schema(schema_path)
		validator = Draft202012Validator(schema)
		errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

		if errors:
			print(f"\n❌ {name or data_path} failed schema validation:")
			for e in errors:
				location = " → ".join(str(x) for x in e.absolute_path) or "<root>"
				print(f"   • {location}: {e.message}")
		else:
			print(f"✅ {name or data_path} passed validation.")

	except FileNotFoundError:
		print(f"⚠️ File not found: {data_path} or {schema_path}")
	except ValidationError as e:
		print(f"❌ {name or data_path} failed: {e.message}")
	except Exception as e:
		print(f"⚠️ Unexpected error validating {name or data_path}: {e}")
