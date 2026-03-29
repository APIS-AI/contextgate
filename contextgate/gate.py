from __future__ import annotations

import json
from typing import Any

from .assembler import assemble_hud
from .parser import parse_envelope
from .schemas import HudSchema, parse_hud_schema
from .update_channel import extract_update, strip_update


class ContextGate:
    def __init__(self, default_hud_schema: HudSchema | dict[str, Any] | None = None) -> None:
        if isinstance(default_hud_schema, dict):
            self.default_hud_schema = parse_hud_schema(default_hud_schema)
        else:
            self.default_hud_schema = default_hud_schema
        self.active_hud: dict[str, Any] = {"mode": "replace", "fields": {}}

    def register_hud_schema(self, payload: dict[str, Any] | None) -> HudSchema | None:
        schema = parse_hud_schema(payload)
        if schema is not None:
            self.default_hud_schema = schema
        return self.default_hud_schema

    def assemble_hud(self, hud_values: dict[str, Any] | None) -> dict[str, Any]:
        self.active_hud = assemble_hud(hud_values, self.default_hud_schema)
        return self.active_hud

    def parse_envelope(self, envelope: dict[str, Any]) -> dict[str, Any]:
        return parse_envelope(envelope, default_hud_schema=self.default_hud_schema)

    def build_envelope(
        self,
        *,
        hud: dict[str, Any] | None = None,
        content: list[dict[str, Any]] | None = None,
        transcript: list[str] | None = None,
        auth: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "ctx_version": "0.1",
            "auth": {
                "source": (auth or {}).get("source", "local_runtime"),
                "trust": (auth or {}).get("trust", "trusted"),
            },
            "hud": hud,
            "content": content or [],
            "transcript": transcript or [],
        }

    def render(
        self,
        *,
        base_prompt: str,
        hud: dict[str, Any] | None = None,
        content: list[dict[str, Any]] | None = None,
        transcript: list[str] | None = None,
        auth: dict[str, Any] | None = None,
    ) -> str:
        envelope = self.build_envelope(
            hud=hud,
            content=content,
            transcript=transcript,
            auth=auth,
        )
        return "\n".join(
            [
                base_prompt.rstrip(),
                "",
                "<CONTEXTGATE_ENVELOPE>",
                json.dumps(envelope, indent=2, sort_keys=True),
                "</CONTEXTGATE_ENVELOPE>",
            ]
        )

    def extract_update(self, response: str) -> dict[str, Any] | None:
        return extract_update(response)

    def apply_update(self, update: dict[str, Any] | None) -> None:
        if not update:
            return
        hud = update.get("hud")
        if isinstance(hud, dict):
            self.assemble_hud(hud)

    def visible_text(self, response: str) -> str:
        return strip_update(response)
