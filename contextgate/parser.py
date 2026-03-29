from __future__ import annotations

import json
import re
from typing import Any

from .assembler import assemble_hud
from .schemas import HudSchema, ValidationError, parse_hud_schema

ENVELOPE_BLOCK_RE = re.compile(
    r"<CONTEXTGATE_ENVELOPE>\s*(?P<payload>.*?)\s*</CONTEXTGATE_ENVELOPE>",
    re.DOTALL,
)


class EnvelopeParseError(ValueError):
    pass


def parse_envelope(
    envelope: dict[str, Any] | str,
    *,
    default_hud_schema: HudSchema | None = None,
    on_unknown_hud: str = "ignore",
) -> dict[str, Any]:
    if isinstance(envelope, str):
        envelope = extract_envelope(envelope)

    auth = envelope.get("auth") or {}
    schema = default_hud_schema
    if "hud_schema" in envelope:
        schema = parse_hud_schema(envelope.get("hud_schema")) or default_hud_schema

    raw_hud = envelope.get("hud") or {}
    if isinstance(raw_hud, dict) and "fields" in raw_hud and isinstance(raw_hud.get("fields"), dict):
        hud_values = raw_hud.get("fields")
    else:
        hud_values = raw_hud

    parsed = {
        "ctx_version": envelope.get("ctx_version", "0.1"),
        "auth": {
            "source": auth.get("source", "unknown"),
            "trust": auth.get("trust", "untrusted"),
        },
        "hud": assemble_hud(hud_values, schema, on_unknown=on_unknown_hud),
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


def extract_envelope(prompt_text: str) -> dict[str, Any]:
    match = ENVELOPE_BLOCK_RE.search(prompt_text)
    if not match:
        raise EnvelopeParseError("No CONTEXTGATE envelope block found")

    payload = match.group("payload")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise EnvelopeParseError("Invalid CONTEXTGATE envelope payload") from exc

    if not isinstance(parsed, dict):
        raise EnvelopeParseError("Envelope payload must be an object")

    return parsed
