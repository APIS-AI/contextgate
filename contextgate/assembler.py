from __future__ import annotations

from typing import Any

from .schemas import HudSchema, ValidationError, validate_by_spec


def assemble_hud(
    hud_values: dict[str, Any] | None,
    schema: HudSchema | None,
    *,
    on_unknown: str = "ignore",
) -> dict[str, Any]:
    hud_values = hud_values or {}
    if schema is None:
        return {"mode": "replace", "fields": dict(hud_values)}

    normalized: dict[str, Any] = {}
    for name, value in hud_values.items():
        spec = schema.fields.get(name)
        if spec is None:
            if on_unknown == "ignore":
                continue
            if on_unknown == "reject":
                raise ValidationError(f"Unknown HUD field: {name}")
            raise ValidationError(f"Unsupported on_unknown mode: {on_unknown}")
        normalized[name] = validate_by_spec(spec, value)

    return {"mode": "replace", "fields": normalized}
