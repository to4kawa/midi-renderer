from __future__ import annotations

from pathlib import Path
from typing import Any


class LoaderError(ValueError):
    """Raised when YAML loading fails or input is invalid."""


def _parse_scalar(value: str) -> Any:
    stripped = value.strip()
    if stripped in {"[]", "[ ]"}:
        return []
    if stripped.startswith("'") and stripped.endswith("'"):
        return stripped[1:-1]
    if stripped.startswith('"') and stripped.endswith('"'):
        return stripped[1:-1]
    if stripped.isdigit():
        return int(stripped)
    return stripped


def _minimal_yaml_parse(text: str) -> dict[str, Any]:
    """Very small YAML subset parser for bootstrap tests.

    Supports top-level keys and single-level nested mappings.
    """
    result: dict[str, Any] = {}
    current_parent: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if line.startswith("  "):
            if current_parent is None:
                raise LoaderError("Invalid indentation in YAML")
            key, sep, value = line.strip().partition(":")
            if not sep:
                raise LoaderError(f"Invalid YAML line: {raw_line}")
            parent = result.get(current_parent)
            if not isinstance(parent, dict):
                raise LoaderError("Nested YAML entry without mapping parent")
            parent[key.strip()] = _parse_scalar(value)
            continue

        key, sep, value = line.partition(":")
        if not sep:
            raise LoaderError(f"Invalid YAML line: {raw_line}")

        key = key.strip()
        value = value.strip()
        if value == "":
            result[key] = {}
            current_parent = key
        else:
            result[key] = _parse_scalar(value)
            current_parent = None

    return result


def load_yaml(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise LoaderError(f"YAML file does not exist: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return {}

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ModuleNotFoundError:
        data = _minimal_yaml_parse(text)

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise LoaderError(f"YAML root must be a mapping: {file_path}")
    return data


def load_render_spec(path: str | Path) -> dict[str, Any]:
    return load_yaml(path)


def load_optional_meta(path: str | Path) -> dict[str, Any] | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    return load_yaml(file_path)
