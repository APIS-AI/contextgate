from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FieldSpec:
    expected_type: str


@dataclass(frozen=True)
class HudSchema:
    version: str
    fields: dict[str, FieldSpec]


class ValidationError(ValueError):
    pass


SCALAR_TYPES = {"string", "integer", "boolean", "timestamp"}


def parse_hud_schema(payload: dict[str, Any] | None) -> HudSchema | None:
    if payload is None:
        return None
    version = payload.get("version", "v0")
    raw_fields = payload.get("fields", {})
    fields: dict[str, FieldSpec] = {}
    for name, spec in raw_fields.items():
        expected_type = spec.get("expected_type")
        if not isinstance(expected_type, str) or not expected_type:
            raise ValidationError(f"Field {name!r} is missing expected_type")
        fields[name] = FieldSpec(expected_type=expected_type)
    return HudSchema(version=version, fields=fields)


def validate_value(expected_type: str, value: Any) -> Any:
    if expected_type.endswith("[]"):
        if not isinstance(value, list):
            raise ValidationError(f"Expected list for {expected_type}")
        inner_type = expected_type[:-2]
        return [validate_value(inner_type, item) for item in value]

    if expected_type == "string":
        if not isinstance(value, str):
            raise ValidationError("Expected string")
        return value

    if expected_type == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("Expected integer")
        return value

    if expected_type == "boolean":
        if not isinstance(value, bool):
            raise ValidationError("Expected boolean")
        return value

    if expected_type == "timestamp":
        if not isinstance(value, str):
            raise ValidationError("Expected timestamp string")
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("Expected RFC3339/ISO8601 timestamp") from exc
        return value

    raise ValidationError(f"Unsupported expected_type: {expected_type}")
