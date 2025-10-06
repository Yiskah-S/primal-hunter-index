import json
from pathlib import Path
from typing import Any, Union

from jsonschema import Draft202012Validator, ValidationError

from core.io_safe import write_json_atomic as _write_json_atomic


def read_json(path: Union[str, Path]) -> Any:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def write_json_atomic(path: Union[str, Path], data: Any) -> None:
    _write_json_atomic(path, data)

def load_schema(path: Union[str, Path]) -> dict[str, Any]:
    return read_json(path)


def validate_instance(instance: Any, schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        msg = "\n".join(
            f"- {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
        )
        raise ValueError(f"Schema validation failed:\n{msg}")


def validate_json_schema(
    data_path: Path, schema_path: Path
) -> list[ValidationError]:
    data_path = Path(data_path)
    schema_path = Path(schema_path)

    missing = [p for p in (data_path, schema_path) if not p.exists()]
    if missing:
        missing_str = ", ".join(str(p) for p in missing)
        raise FileNotFoundError(f"Missing file(s): {missing_str}")

    data = read_json(data_path)
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    return sorted(validator.iter_errors(data), key=lambda e: e.path)

def validate_json_file(data: Any, schema_path: Path) -> None:
    """
    Lightweight inline validator for tools.
    Raises ValueError if validation fails.
    """
    schema = load_schema(schema_path)
    validate_instance(data, schema)

def load_json(path: Path) -> dict:
	if path.stat().st_size == 0:
		return {}
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)
