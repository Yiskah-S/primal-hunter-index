import json
import warnings
from pathlib import Path
from typing import Any, Union

try:
    from jsonschema import Draft202012Validator, RefResolver, ValidationError
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    Draft202012Validator = None  # type: ignore[assignment]
    RefResolver = None  # type: ignore[assignment]
    ValidationError = Exception  # type: ignore[assignment]
    _JSONSCHEMA_IMPORT_ERROR = exc
else:
    _JSONSCHEMA_IMPORT_ERROR = None

from core.io_safe import write_json_atomic as _write_json_atomic

_SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
_SHARED_SCHEMA_URIS = {
    "https://primal-hunter.local/schemas/shared/granted_by.schema.json": _SCHEMA_ROOT
    / "shared"
    / "granted_by.schema.json",
    "https://primal-hunter.local/schemas/shared/flavor.schema.json": _SCHEMA_ROOT
    / "shared"
    / "flavor.schema.json",
    "https://primal-hunter.local/schemas/shared/resource_block.schema.json": _SCHEMA_ROOT
    / "shared"
    / "resource_block.schema.json",
    "https://primal-hunter.local/schemas/shared/tags.schema.json": _SCHEMA_ROOT
    / "shared"
    / "tags.schema.json",
    "https://primal-hunter.local/schemas/shared/provenance.schema.json": _SCHEMA_ROOT
    / "shared"
    / "provenance.schema.json",
    "https://primal-hunter.local/schemas/shared/source_ref.schema.json": _SCHEMA_ROOT
    / "shared"
    / "source_ref.schema.json",
    "https://primal-hunter.local/schemas/shared/id.schema.json": _SCHEMA_ROOT
    / "shared"
    / "id.schema.json",
    "https://primal-hunter.local/schemas/shared/param_rule.schema.json": _SCHEMA_ROOT
    / "shared"
    / "param_rule.schema.json",
    "https://primal-hunter.local/schemas/shared/record_log.schema.json": _SCHEMA_ROOT
    / "shared"
    / "record_log.schema.json",
    "https://primal-hunter.local/schemas/timeline_event.schema.json": _SCHEMA_ROOT
    / "timeline_event.schema.json",
    "https://primal-hunter.local/schemas/skill_node.schema.json": _SCHEMA_ROOT
    / "skill_node.schema.json",
}

_SHARED_SCHEMA_STORE = {}
_JSONSCHEMA_AVAILABLE = Draft202012Validator is not None
_WARNED_JSONSCHEMA_MISSING = False


def _load_shared_store() -> dict[str, Any]:
    store: dict[str, Any] = {}
    for uri, path in _SHARED_SCHEMA_URIS.items():
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                store[uri] = json.load(handle)
    return store


_SHARED_SCHEMA_STORE = _load_shared_store()


def _warn_jsonschema_missing() -> None:
    global _WARNED_JSONSCHEMA_MISSING
    if _WARNED_JSONSCHEMA_MISSING:
        return
    warnings.warn(
        "jsonschema is not installed; skipping schema validation. "
        "Run `pip install -r requirements/requirements-schema.txt` to enable full validation.",
        RuntimeWarning,
        stacklevel=3,
    )
    _WARNED_JSONSCHEMA_MISSING = True


def _build_validator(schema: dict[str, Any]) -> Draft202012Validator:
    if not _JSONSCHEMA_AVAILABLE:
        raise RuntimeError(
            "jsonschema package is required for schema validation"
        ) from _JSONSCHEMA_IMPORT_ERROR
    resolver = RefResolver.from_schema(schema, store=_SHARED_SCHEMA_STORE)
    return Draft202012Validator(schema, resolver=resolver)


def read_json(path: Union[str, Path]) -> Any:
    path_obj = Path(path)
    return json.loads(path_obj.read_text(encoding="utf-8")) if path_obj.exists() else {}


def write_json_atomic(path: Union[str, Path], data: Any) -> None:
    _write_json_atomic(path, data)


def load_schema(path: Union[str, Path]) -> dict[str, Any]:
    return read_json(path)


def validate_instance(instance: Any, schema: dict[str, Any]) -> None:
    if not _JSONSCHEMA_AVAILABLE:
        _warn_jsonschema_missing()
        return
    validator = _build_validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        msg = "\n".join(
            f"- {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
        )
        raise ValueError(f"Schema validation failed:\n{msg}")


def validate_json_schema(data_path: Path, schema_path: Path) -> list[ValidationError]:
    data_path = Path(data_path)
    schema_path = Path(schema_path)

    missing = [p for p in (data_path, schema_path) if not p.exists()]
    if missing:
        missing_str = ", ".join(str(p) for p in missing)
        raise FileNotFoundError(f"Missing file(s): {missing_str}")

    if not _JSONSCHEMA_AVAILABLE:
        _warn_jsonschema_missing()
        return []

    data = read_json(data_path)
    schema = load_schema(schema_path)
    validator = _build_validator(schema)
    return sorted(validator.iter_errors(data), key=lambda e: e.path)


def validate_json_file(data: Any, schema_path: Path) -> None:
    """
    Lightweight inline validator for tools.
    Raises ValueError if validation fails.
    """
    if not _JSONSCHEMA_AVAILABLE:
        _warn_jsonschema_missing()
        return
    schema = load_schema(schema_path)
    validate_instance(data, schema)


def load_json(path: Path) -> dict:
    if path.stat().st_size == 0:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
