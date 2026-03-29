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
        self.active_content: list[dict[str, Any]] = []
        self.active_transcript: list[str] = []

    def register_hud_schema(self, payload: dict[str, Any] | None) -> HudSchema | None:
        schema = parse_hud_schema(payload)
        if schema is not None:
            self.default_hud_schema = schema
        return self.default_hud_schema

    def assemble_hud(self, hud_values: dict[str, Any] | None) -> dict[str, Any]:
        self.active_hud = assemble_hud(hud_values, self.default_hud_schema)
        return self.active_hud

    def parse_envelope(self, envelope: dict[str, Any] | str) -> dict[str, Any]:
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
            "hud": hud if hud is not None else dict(self.active_hud),
            "content": content if content is not None else list(self.active_content),
            "transcript": transcript if transcript is not None else list(self.active_transcript),
        }

    def render(
        self,
        *,
        base_prompt: str,
        hud: dict[str, Any] | None = None,
        content: list[dict[str, Any]] | None = None,
        transcript: list[str] | None = None,
        auth: dict[str, Any] | None = None,
        compact: bool = False,
    ) -> str:
        envelope = self.build_envelope(
            hud=hud,
            content=content,
            transcript=transcript,
            auth=auth,
        )
        json_kwargs = {"sort_keys": True}
        if compact:
            payload = json.dumps(envelope, separators=(",", ":"), **json_kwargs)
        else:
            payload = json.dumps(envelope, indent=2, **json_kwargs)
        return "\n".join(
            [
                base_prompt.rstrip(),
                "",
                "<CONTEXTGATE_ENVELOPE>",
                payload,
                "</CONTEXTGATE_ENVELOPE>",
            ]
        )

    def extract_update(self, response: str) -> dict[str, Any] | None:
        return extract_update(response, hud_schema=self.default_hud_schema)

    def apply_update(self, update: dict[str, Any] | None) -> None:
        if not update:
            return
        raw_hud = update.get("hud")
        if not isinstance(raw_hud, dict):
            raw_hud = None

        if raw_hud is not None:
            if "fields" in raw_hud and isinstance(raw_hud.get("fields"), dict):
                mode = raw_hud.get("mode", "replace")
                hud_values = raw_hud["fields"]
            else:
                mode = "replace"
                hud_values = raw_hud

            normalized = assemble_hud(hud_values, self.default_hud_schema)
            if mode == "merge":
                merged_fields = dict(self.active_hud.get("fields", {}))
                merged_fields.update(normalized["fields"])
                self.active_hud = {"mode": "replace", "fields": merged_fields}
            else:
                if mode != "replace":
                    raise ValueError(f"Unsupported HUD update mode: {mode}")
                self.active_hud = normalized

        if "content" in update:
            self.active_content = list(update["content"])

        if "transcript" in update:
            self.active_transcript = list(update["transcript"])

    def visible_text(self, response: str) -> str:
        return strip_update(response)
