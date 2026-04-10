from __future__ import annotations

import json
from typing import Any

from .assembler import assemble_hud
from .parser import parse_envelope
from .schemas import HudSchema, parse_hud_schema
from .update_channel import extract_update, strip_update


class ContextGate:
    def __init__(
        self,
        default_hud_schema: HudSchema | dict[str, Any] | None = None,
        *,
        content_limit: int | None = None,
        transcript_limit: int | None = None,
        dedupe_content: bool = False,
        dedupe_transcript: bool = False,
        content_overflow: str = "truncate",
        transcript_overflow: str = "truncate",
    ) -> None:
        if isinstance(default_hud_schema, dict):
            self.default_hud_schema = parse_hud_schema(default_hud_schema)
        else:
            self.default_hud_schema = default_hud_schema
        self.content_limit = content_limit
        self.transcript_limit = transcript_limit
        self.dedupe_content = dedupe_content
        self.dedupe_transcript = dedupe_transcript
        self.content_overflow = content_overflow
        self.transcript_overflow = transcript_overflow
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
            "content": self._apply_content_policy(content if content is not None else self.active_content),
            "transcript": self._apply_transcript_policy(
                transcript if transcript is not None else self.active_transcript
            ),
        }

    def _apply_content_policy(
        self, items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        normalized = list(items)
        if self.dedupe_content:
            deduped: list[dict[str, Any]] = []
            seen: set[str] = set()
            for item in normalized:
                marker = json.dumps(item, sort_keys=True)
                if marker in seen:
                    continue
                seen.add(marker)
                deduped.append(item)
            normalized = deduped
        if self.content_limit is not None:
            overflow = len(normalized) - self.content_limit
            if overflow > 0:
                if self.content_overflow == "truncate":
                    normalized = normalized[-self.content_limit :]
                elif self.content_overflow == "reject":
                    raise ValueError(
                        f"Content limit exceeded by {overflow} item(s)"
                    )
                else:
                    raise ValueError(
                        f"Unsupported content overflow policy: {self.content_overflow}"
                    )
        return normalized

    def _apply_transcript_policy(self, items: list[str]) -> list[str]:
        normalized = list(items)
        if self.dedupe_transcript:
            deduped: list[str] = []
            seen: set[str] = set()
            for item in normalized:
                if item in seen:
                    continue
                seen.add(item)
                deduped.append(item)
            normalized = deduped
        if self.transcript_limit is not None:
            overflow = len(normalized) - self.transcript_limit
            if overflow > 0:
                if self.transcript_overflow == "truncate":
                    normalized = normalized[-self.transcript_limit :]
                elif self.transcript_overflow == "reject":
                    raise ValueError(
                        f"Transcript limit exceeded by {overflow} item(s)"
                    )
                else:
                    raise ValueError(
                        "Unsupported transcript overflow policy: "
                        f"{self.transcript_overflow}"
                    )
        return normalized

    def render(
        self,
        *,
        base_prompt: str,
        hud: dict[str, Any] | None = None,
        content: list[dict[str, Any]] | None = None,
        transcript: list[str] | None = None,
        auth: dict[str, Any] | None = None,
        compact: bool = False,
        tag: str = "CONTEXTGATE_ENVELOPE",
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
                f"<{tag}>",
                payload,
                f"</{tag}>",
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
            raw_content = update["content"]
            if isinstance(raw_content, dict):
                content_mode = raw_content.get("mode", "replace")
                content_items = list(raw_content.get("items", []))
                if content_mode == "merge":
                    self.active_content.extend(content_items)
                else:
                    if content_mode != "replace":
                        raise ValueError(f"Unsupported content update mode: {content_mode}")
                    self.active_content = content_items
            else:
                self.active_content = list(raw_content)
            self.active_content = self._apply_content_policy(self.active_content)

        if "transcript" in update:
            raw_transcript = update["transcript"]
            if isinstance(raw_transcript, dict):
                transcript_mode = raw_transcript.get("mode", "replace")
                transcript_items = list(raw_transcript.get("items", []))
                if transcript_mode == "merge":
                    self.active_transcript.extend(transcript_items)
                else:
                    if transcript_mode != "replace":
                        raise ValueError(
                            f"Unsupported transcript update mode: {transcript_mode}"
                        )
                    self.active_transcript = transcript_items
            else:
                self.active_transcript = list(raw_transcript)
            self.active_transcript = self._apply_transcript_policy(self.active_transcript)

    def visible_text(self, response: str) -> str:
        return strip_update(response)
