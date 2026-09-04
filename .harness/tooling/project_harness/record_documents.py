from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class MarkdownRecordError(ValueError):
    """Raised when canonical Markdown record front matter is malformed."""


_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def _scalar(value: Any) -> str:
    if isinstance(value, (dict, list)) and value:
        raise MarkdownRecordError("nonempty containers must use indented blocks")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _dump(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if not isinstance(key, str) or _KEY.fullmatch(key) is None:
                raise MarkdownRecordError(f"unsupported front matter key: {key!r}")
            if isinstance(child, (dict, list)) and child:
                lines.append(f"{prefix}{key}:")
                lines.extend(_dump(child, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_scalar(child)}")
        return lines
    if isinstance(value, list):
        lines = []
        for child in value:
            if isinstance(child, (dict, list)) and child:
                lines.append(f"{prefix}-")
                lines.extend(_dump(child, indent + 2))
            else:
                lines.append(f"{prefix}- {_scalar(child)}")
        return lines
    raise MarkdownRecordError("front matter root must be an object or array")


def _parse_scalar(value: str, line_number: int) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise MarkdownRecordError(
            f"front matter line {line_number} has an invalid scalar: {exc.msg}"
        ) from exc


def _parse_front_matter(value: str) -> dict[str, Any]:
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw in enumerate(value.split("\n"), start=2):
        if not raw.strip():
            continue
        if "\t" in raw:
            raise MarkdownRecordError(
                f"front matter line {line_number} must not contain tabs"
            )
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise MarkdownRecordError(
                f"front matter line {line_number} must use two-space indentation"
            )
        tokens.append((indent, raw[indent:], line_number))
    if not tokens:
        raise MarkdownRecordError("front matter must not be empty")

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(tokens) or tokens[index][0] != indent:
            line = tokens[index][2] if index < len(tokens) else "EOF"
            raise MarkdownRecordError(
                f"front matter line {line} has an unexpected indentation"
            )
        is_list = tokens[index][1] == "-" or tokens[index][1].startswith("- ")
        container: Any = [] if is_list else {}
        while index < len(tokens):
            current_indent, content, line_number = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise MarkdownRecordError(
                    f"front matter line {line_number} has an unexpected indentation"
                )
            item_is_list = content == "-" or content.startswith("- ")
            if item_is_list != is_list:
                raise MarkdownRecordError(
                    f"front matter line {line_number} mixes object and array entries"
                )
            if is_list:
                tail = content[1:].strip()
                index += 1
                if tail:
                    container.append(_parse_scalar(tail, line_number))
                    continue
                if index >= len(tokens) or tokens[index][0] != indent + 2:
                    raise MarkdownRecordError(
                        f"front matter line {line_number} requires an indented value"
                    )
                child, index = parse_block(index, indent + 2)
                container.append(child)
                continue

            key, separator, tail = content.partition(":")
            if not separator or _KEY.fullmatch(key) is None:
                raise MarkdownRecordError(
                    f"front matter line {line_number} has an invalid key"
                )
            if key in container:
                raise MarkdownRecordError(
                    f"front matter line {line_number} duplicates key {key!r}"
                )
            tail = tail.strip()
            index += 1
            if tail:
                container[key] = _parse_scalar(tail, line_number)
                continue
            if index >= len(tokens) or tokens[index][0] != indent + 2:
                raise MarkdownRecordError(
                    f"front matter line {line_number} requires an indented value"
                )
            container[key], index = parse_block(index, indent + 2)
        return container, index

    parsed, consumed = parse_block(0, 0)
    if consumed != len(tokens):
        raise MarkdownRecordError(
            f"front matter line {tokens[consumed][2]} was not consumed"
        )
    if not isinstance(parsed, dict):
        raise MarkdownRecordError("front matter root must be an object")
    return parsed


def read_markdown_record(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise MarkdownRecordError(f"missing Markdown record: {path}") from exc
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        raise MarkdownRecordError("Markdown record must start with '---'")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise MarkdownRecordError("Markdown record front matter is not closed") from exc
    metadata = _parse_front_matter("\n".join(lines[1:closing]))
    body = "\n".join(lines[closing + 1 :])
    return metadata, body


def render_markdown_record(record: dict[str, Any], body: str | None = None) -> str:
    metadata = "\n".join(_dump(record))
    if body is None or not body.strip():
        identifier = str(record.get("id", "Record"))
        title = str(record.get("title") or record.get("kind") or "Record")
        body = (
            f"# {identifier}: {title}\n\n"
            "Canonical fields are stored in the front matter above. "
            "Human-readable notes may be added below.\n"
        )
    elif not body.endswith("\n"):
        body += "\n"
    return f"---\n{metadata}\n---\n{body}"
