from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FieldSpec:
    expected_type: str | None = None
    expected_schema: str | None = None


@dataclass(frozen=True)
class HudSchema:
    version: str
    fields: dict[str, FieldSpec]


class ValidationError(ValueError):
    pass


REQUIRED_IMAGE_REF_FIELDS = {
    "uri": str,
    "mime_type": str,
    "sha256": str,
}
REQUIRED_AUDIO_REF_FIELDS = {
    "uri": str,
    "mime_type": str,
    "sha256": str,
    "duration_ms": int,
}


def parse_hud_schema(payload: dict[str, Any] | None) -> HudSchema | None:
    if payload is None:
        return None
    version = payload.get("version", "v0")
    raw_fields = payload.get("fields", {})
    fields: dict[str, FieldSpec] = {}
    for name, spec in raw_fields.items():
        expected_type = spec.get("expected_type")
        expected_schema = spec.get("expected_schema")
        if not isinstance(expected_type, str):
            expected_type = None
        if not isinstance(expected_schema, str):
            expected_schema = None
        if not expected_type and not expected_schema:
            raise ValidationError(
                f"Field {name!r} must declare expected_type or expected_schema"
            )
        fields[name] = FieldSpec(
            expected_type=expected_type,
            expected_schema=expected_schema,
        )
    return HudSchema(version=version, fields=fields)


def validate_by_spec(spec: FieldSpec, value: Any) -> Any:
    if spec.expected_type:
        return validate_type_value(spec.expected_type, value)
    if spec.expected_schema:
        return validate_schema_value(spec.expected_schema, value)
    raise ValidationError("FieldSpec must declare expected_type or expected_schema")


def validate_type_value(expected_type: str, value: Any) -> Any:
    if expected_type.endswith("[]"):
        if not isinstance(value, list):
            raise ValidationError(f"Expected list for {expected_type}")
        inner_type = expected_type[:-2]
        return [validate_type_value(inner_type, item) for item in value]

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


def validate_schema_value(expected_schema: str, value: Any) -> Any:
    if expected_schema == "ImageRefV1":
        return _validate_record(expected_schema, value, REQUIRED_IMAGE_REF_FIELDS)
    if expected_schema == "AudioRefV1":
        return _validate_record(expected_schema, value, REQUIRED_AUDIO_REF_FIELDS)
    raise ValidationError(f"Unsupported expected_schema: {expected_schema}")


def _validate_record(
    expected_schema: str,
    value: Any,
    required_fields: dict[str, type],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"Expected object for {expected_schema}")
    normalized: dict[str, Any] = {}
    for field_name, field_type in required_fields.items():
        field_value = value.get(field_name)
        if field_value is None:
            raise ValidationError(f"{expected_schema} missing field {field_name!r}")
        if field_type is int:
            if isinstance(field_value, bool) or not isinstance(field_value, int):
                raise ValidationError(f"{expected_schema}.{field_name} must be an integer")
        elif not isinstance(field_value, field_type):
            raise ValidationError(
                f"{expected_schema}.{field_name} must be {field_type.__name__}"
            )
        normalized[field_name] = field_value

    for optional in ("width", "height", "alt", "label"):
        if optional in value:
            normalized[optional] = value[optional]

    return normalized
