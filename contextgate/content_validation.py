from __future__ import annotations

from typing import Any

from .schemas import ValidationError


ALLOWED_CONTENT_TRUST = {"trusted", "untrusted"}
ALLOWED_FIELD_CLASSES = {"display_text", "message_text", "status_text", "label_text"}


def normalize_content_items(
    payload: Any, *, error_cls: type[Exception] = ValidationError
) -> list[dict[str, str]]:
    if not isinstance(payload, list):
        raise error_cls("Content update payload must be a list")

    normalized: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise error_cls("Content items must be objects")
        extra_keys = set(item) - {"label", "field_class", "trust", "value"}
        if extra_keys:
            names = ", ".join(sorted(extra_keys))
            raise error_cls(f"Unsupported content item keys: {names}")

        label = item.get("label", "content")
        field_class = item.get("field_class", "display_text")
        trust = item.get("trust", "untrusted")
        value = item.get("value", "")
        if not all(isinstance(field, str) for field in (label, field_class, trust, value)):
            raise error_cls("Content item fields must be strings")
        if trust not in ALLOWED_CONTENT_TRUST:
            raise error_cls("Content item trust must be trusted or untrusted")
        if field_class not in ALLOWED_FIELD_CLASSES:
            raise error_cls(
                "Content item field_class must be one of: "
                + ", ".join(sorted(ALLOWED_FIELD_CLASSES))
            )

        normalized.append(
            {
                "label": label,
                "field_class": field_class,
                "trust": trust,
                "value": value,
            }
        )
    return normalized
