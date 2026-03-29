from __future__ import annotations

from typing import Any

from .assembler import assemble_hud
from .schemas import HudSchema, parse_hud_schema


def parse_envelope(
    envelope: dict[str, Any],
    *,
    default_hud_schema: HudSchema | None = None,
    on_unknown_hud: str = "ignore",
) -> dict[str, Any]:
    auth = envelope.get("auth") or {}
    schema = default_hud_schema
    if "hud_schema" in envelope:
        schema = parse_hud_schema(envelope.get("hud_schema")) or default_hud_schema

    parsed = {
        "ctx_version": envelope.get("ctx_version", "0.1"),
        "auth": {
            "source": auth.get("source", "unknown"),
            "trust": auth.get("trust", "untrusted"),
        },
        "hud": assemble_hud(envelope.get("hud"), schema, on_unknown=on_unknown_hud),
        "content": [],
        "transcript": list(envelope.get("transcript") or []),
    }

    for item in envelope.get("content") or []:
        parsed["content"].append(
            {
                "label": item.get("label", "content"),
                "field_class": item.get("field_class", "display_text"),
                "trust": item.get("trust", "untrusted"),
                "value": item.get("value", ""),
            }
        )

    return parsed
