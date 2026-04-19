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

    Supports mappings and list items used by bootstrap render specs.
    """
    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        lines.append((indent, raw_line[indent:].rstrip()))

    if not lines:
        return {}

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    for index, (indent, content) in enumerate(lines):
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]
        next_indent = lines[index + 1][0] if index + 1 < len(lines) else -1

        if content.startswith("- "):
            if not isinstance(parent, list):
                raise LoaderError(f"Invalid list item placement: {content}")

            item_content = content[2:].strip()
            if ":" in item_content:
                key, sep, value = item_content.partition(":")
                if not sep:
                    raise LoaderError(f"Invalid YAML line: {content}")
                item: dict[str, Any] = {}
                if value.strip():
                    item[key.strip()] = _parse_scalar(value)
                    parent.append(item)
                else:
                    nested: dict[str, Any] = {}
                    item[key.strip()] = nested
                    parent.append(item)
                    stack.append((indent, nested))
                if next_indent > indent and value.strip():
                    stack.append((indent, item))
            elif item_content:
                parent.append(_parse_scalar(item_content))
            else:
                nested_item: dict[str, Any] = {}
                parent.append(nested_item)
                stack.append((indent, nested_item))
            continue

        key, sep, value = content.partition(":")
        if not sep:
            raise LoaderError(f"Invalid YAML line: {content}")

        key = key.strip()
        value = value.strip()
        if not isinstance(parent, dict):
            raise LoaderError(f"Invalid mapping placement: {content}")

        if value:
            parent[key] = _parse_scalar(value)
            continue

        container: Any = [] if next_indent > indent and lines[index + 1][1].startswith("- ") else {}
        parent[key] = container
        stack.append((indent, container))

    return root


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
