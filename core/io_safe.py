#!/usr/bin/env python3
"""Safe filesystem helpers for atomic JSON writes."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Union


def open_directory_descriptor(path: Path) -> int:
    """Return an open dir fd for fsync; caller must close."""
    parent_directory_descriptor = os.open(path, os.O_DIRECTORY)
    return parent_directory_descriptor


def write_json_atomic(path: Union[str, Path], data: Any, *, backup: bool = False, ensure_ascii: bool = False) -> None:
    """Write JSON to *path* atomically using a temp file in the same directory.

    Args:
        path: Target file path.
        data: JSON-serialisable payload.
        backup: When True, keep a timestamp-less `.bak` copy of the previous file.
        ensure_ascii: Pass-through to `json.dump`.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    parent_directory_descriptor: Optional[int] = None
    temp_file_descriptor = None
    temp_path: Optional[Path] = None
    try:
        temp_file_descriptor, temp_name = tempfile.mkstemp(prefix=".temp.", dir=path.parent)
        temp_path = Path(temp_name)
        with os.fdopen(temp_file_descriptor, "w", encoding="utf-8", newline="") as temp_file_handle:
            json.dump(data, temp_file_handle, indent="\t", ensure_ascii=ensure_ascii)
            temp_file_handle.flush()
            os.fsync(temp_file_handle.fileno())
            # file descriptor is closed by context manager; mark descriptor as handled
            temp_file_descriptor = None

            if backup and path.exists():
                backup_path = path.with_suffix(path.suffix + ".bak")
                with path.open("rb") as original_file, backup_path.open("wb") as backup_file:
                    backup_file.write(original_file.read())

        os.replace(temp_path, path)

        parent_directory_descriptor = open_directory_descriptor(path.parent)
        os.fsync(parent_directory_descriptor)

    except Exception:
        # clean up temp file if replace failed
        if temp_file_descriptor is not None:
            os.close(temp_file_descriptor)
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise

    finally:
        if parent_directory_descriptor is not None:
            os.close(parent_directory_descriptor)

def write_json_atomic_safe(path: Union[str, Path], data: Any, schema_path: Union[str, Path], *, backup: bool = False,
    ensure_ascii: bool = False,
) -> None:
    """Validate data against a schema and atomically write to disk if valid."""
    from core.schema_utils import load_schema, validate_instance

    schema = load_schema(schema_path)
    validate_instance(data, schema)
    write_json_atomic(path, data, backup=backup, ensure_ascii=ensure_ascii)
