from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_FILES = {
    "project": "project.schema.json",
    "state": "state.schema.json",
    "source": "source.schema.json",
    "artifact": "artifact.schema.json",
    "requirement": "requirement.schema.json",
    "feature": "feature.schema.json",
    "plan": "plan.schema.json",
    "work_item": "work-item.schema.json",
    "open_item": "open-item.schema.json",
    "evidence": "evidence.schema.json",
    "approval": "approval.schema.json",
    "change": "change.schema.json",
    "result": "result.schema.json",
    "review": "review.schema.json",
    "handoff": "handoff.schema.json",
    "recovery": "recovery.schema.json",
    "claim": "claim.schema.json",
    "authority": "authority.schema.json",
    "event": "event.schema.json",
}


class SchemaSet:
    """Validate the JSON-Schema subset used by this distribution.

    The project intentionally has no third-party runtime dependency.  This
    evaluator implements every keyword used in ``schemas/*.json`` and rejects
    a schema that asks for an unsupported structural keyword instead of
    silently treating that keyword as documentation.
    """

    _SUPPORTED = {
        "$schema",
        "$id",
        "$defs",
        "$ref",
        "type",
        "required",
        "properties",
        "const",
        "enum",
        "pattern",
        "items",
        "minLength",
        "minItems",
        "minimum",
        "oneOf",
        "additionalProperties",
        "format",
    }

    def __init__(self, directory: Path):
        self.directory = directory
        self._cache: dict[Path, dict[str, Any]] = {}

    def _load(self, path: Path) -> dict[str, Any]:
        resolved = path.resolve()
        if resolved in self._cache:
            return self._cache[resolved]
        try:
            value = json.loads(resolved.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot load schema {resolved.name}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"schema {resolved.name} is not an object")
        self._cache[resolved] = value
        return value

    def _resolve_ref(self, current_file: Path, value: str) -> tuple[dict[str, Any], Path]:
        filename, marker, fragment = value.partition("#")
        target_file = (current_file.parent / filename).resolve() if filename else current_file
        target: Any = self._load(target_file)
        if marker and fragment:
            if not fragment.startswith("/"):
                raise ValueError(f"unsupported schema reference fragment: {value}")
            for raw_part in fragment[1:].split("/"):
                part = raw_part.replace("~1", "/").replace("~0", "~")
                if not isinstance(target, dict) or part not in target:
                    raise ValueError(f"unresolved schema reference: {value}")
                target = target[part]
        if not isinstance(target, dict):
            raise ValueError(f"schema reference is not an object: {value}")
        return target, target_file

    @staticmethod
    def _matches_type(instance: Any, expected: str) -> bool:
        return {
            "object": isinstance(instance, dict),
            "array": isinstance(instance, list),
            "string": isinstance(instance, str),
            "integer": isinstance(instance, int) and not isinstance(instance, bool),
            "number": isinstance(instance, (int, float)) and not isinstance(instance, bool),
            "boolean": isinstance(instance, bool),
            "null": instance is None,
        }.get(expected, False)

    def _check(
        self,
        instance: Any,
        schema: dict[str, Any],
        schema_file: Path,
        location: str,
    ) -> list[str]:
        unsupported = sorted(set(schema) - self._SUPPORTED)
        if unsupported:
            return [
                f"{location}: schema uses unsupported keywords: {', '.join(unsupported)}"
            ]

        if "$ref" in schema:
            reference = schema["$ref"]
            if not isinstance(reference, str):
                return [f"{location}: schema $ref must be a string"]
            try:
                target, target_file = self._resolve_ref(schema_file, reference)
            except ValueError as exc:
                return [f"{location}: {exc}"]
            return self._check(instance, target, target_file, location)

        if "oneOf" in schema:
            choices = schema["oneOf"]
            if not isinstance(choices, list) or not choices:
                return [f"{location}: schema oneOf must be a nonempty array"]
            choice_results = [
                self._check(instance, choice, schema_file, location)
                if isinstance(choice, dict)
                else [f"{location}: schema oneOf entry must be an object"]
                for choice in choices
            ]
            if sum(not result for result in choice_results) != 1:
                return [f"{location}: value must satisfy exactly one oneOf branch"]

        expected_types = schema.get("type")
        if expected_types is not None:
            type_names = (
                expected_types if isinstance(expected_types, list) else [expected_types]
            )
            if not type_names or any(not isinstance(item, str) for item in type_names):
                return [f"{location}: schema type must be a string or string array"]
            if not any(self._matches_type(instance, item) for item in type_names):
                return [
                    f"{location}: expected {' or '.join(type_names)}, "
                    f"found {type(instance).__name__}"
                ]

        errors: list[str] = []
        if "const" in schema and instance != schema["const"]:
            errors.append(f"{location}: expected constant {schema['const']!r}")
        if "enum" in schema:
            choices = schema["enum"]
            if not isinstance(choices, list) or instance not in choices:
                errors.append(f"{location}: value is not in the declared enum")

        if isinstance(instance, str):
            minimum_length = schema.get("minLength")
            if isinstance(minimum_length, int) and len(instance) < minimum_length:
                errors.append(f"{location}: string is shorter than {minimum_length}")
            pattern = schema.get("pattern")
            if isinstance(pattern, str) and re.search(pattern, instance) is None:
                errors.append(f"{location}: string does not match {pattern!r}")
            if schema.get("format") == "date-time":
                try:
                    parsed = datetime.fromisoformat(instance.replace("Z", "+00:00"))
                    if parsed.tzinfo is None:
                        raise ValueError("timezone missing")
                except ValueError:
                    errors.append(f"{location}: value is not a timezone-aware date-time")

        if isinstance(instance, int) and not isinstance(instance, bool):
            minimum = schema.get("minimum")
            if isinstance(minimum, (int, float)) and instance < minimum:
                errors.append(f"{location}: number is below minimum {minimum}")

        if isinstance(instance, list):
            minimum_items = schema.get("minItems")
            if isinstance(minimum_items, int) and len(instance) < minimum_items:
                errors.append(f"{location}: array has fewer than {minimum_items} items")
            item_schema = schema.get("items")
            if isinstance(item_schema, dict):
                for index, item in enumerate(instance):
                    errors.extend(
                        self._check(item, item_schema, schema_file, f"{location}[{index}]")
                    )

        if isinstance(instance, dict):
            required = schema.get("required", [])
            if isinstance(required, list):
                for field in required:
                    if isinstance(field, str) and field not in instance:
                        errors.append(f"{location}: missing required property {field}")
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                for field, field_schema in properties.items():
                    if field in instance and isinstance(field_schema, dict):
                        errors.extend(
                            self._check(
                                instance[field],
                                field_schema,
                                schema_file,
                                f"{location}.{field}",
                            )
                        )
            additional = schema.get("additionalProperties", True)
            unknown = set(instance) - set(properties if isinstance(properties, dict) else {})
            if additional is False and unknown:
                errors.append(
                    f"{location}: additional properties are forbidden: "
                    + ", ".join(sorted(unknown))
                )
            elif isinstance(additional, dict):
                for field in sorted(unknown):
                    errors.extend(
                        self._check(
                            instance[field],
                            additional,
                            schema_file,
                            f"{location}.{field}",
                        )
                    )
        return errors

    def validate(self, instance: Any, schema_name: str) -> list[str]:
        schema_file = (self.directory / schema_name).resolve()
        try:
            schema = self._load(schema_file)
        except ValueError as exc:
            return [str(exc)]
        return self._check(instance, schema, schema_file, "$")
