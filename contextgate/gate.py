from __future__ import annotations

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

    def render(
        self,
        *,
        base_prompt: str,
        hud: dict[str, Any] | None = None,
        content: list[dict[str, Any]] | None = None,
        transcript: list[str] | None = None,
    ) -> str:
        sections = [base_prompt.rstrip(), "", "<CONTEXTGATE>"]
        if hud is not None:
            sections.append(f"HUD: {hud}")
        if content:
            sections.append(f"CONTENT: {content}")
        if transcript:
            sections.append(f"TRANSCRIPT: {transcript}")
        sections.append("</CONTEXTGATE>")
        return "\n".join(sections)

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
