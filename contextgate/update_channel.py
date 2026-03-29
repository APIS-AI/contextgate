from __future__ import annotations

import json
import re
from typing import Any

from .assembler import assemble_hud
from .content_validation import normalize_content_items
from .schemas import HudSchema, ValidationError

UPDATE_BLOCK_RE = re.compile(
    r"<CONTEXTGATE_UPDATE>\s*(?P<payload>.*?)\s*</CONTEXTGATE_UPDATE>",
    re.DOTALL,
)


class UpdateChannelError(ValueError):
    pass


def _validate_hud_update(
    payload: Any, hud_schema: HudSchema | None = None
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise UpdateChannelError("HUD update payload must be an object")

    if "fields" in payload:
        fields = payload.get("fields")
        mode = payload.get("mode", "replace")
        if mode not in {"replace", "merge"}:
            raise UpdateChannelError("HUD update mode must be replace or merge")
        if not isinstance(fields, dict):
            raise UpdateChannelError("HUD update fields must be an object")
        extra_keys = set(payload) - {"mode", "fields"}
        if extra_keys:
            names = ", ".join(sorted(extra_keys))
            raise UpdateChannelError(f"Unsupported HUD update keys: {names}")
        try:
            normalized = (
                assemble_hud(fields, hud_schema, on_unknown="reject")["fields"]
                if hud_schema is not None
                else fields
            )
        except ValidationError as exc:
            raise UpdateChannelError(str(exc)) from exc
        return {"mode": mode, "fields": normalized}

    if "mode" in payload:
        raise UpdateChannelError("HUD update mode requires a fields object")

    try:
        return (
            assemble_hud(payload, hud_schema, on_unknown="reject")["fields"]
            if hud_schema is not None
            else payload
        )
    except ValidationError as exc:
        raise UpdateChannelError(str(exc)) from exc


def _validate_content_update(payload: Any) -> dict[str, Any] | list[dict[str, str]]:
    if isinstance(payload, dict):
        mode = payload.get("mode", "replace")
        items = payload.get("items")
        if mode not in {"replace", "merge"}:
            raise UpdateChannelError("Content update mode must be replace or merge")
        if "items" not in payload:
            raise UpdateChannelError("Content update mode requires an items list")
        extra_keys = set(payload) - {"mode", "items"}
        if extra_keys:
            names = ", ".join(sorted(extra_keys))
            raise UpdateChannelError(f"Unsupported content update keys: {names}")
        return {"mode": mode, "items": normalize_content_items(items, error_cls=UpdateChannelError)}

    return normalize_content_items(payload, error_cls=UpdateChannelError)


def _normalize_transcript_items(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        raise UpdateChannelError("Transcript update payload must be a list")
    if not all(isinstance(item, str) for item in payload):
        raise UpdateChannelError("Transcript update items must be strings")
    return list(payload)


def _validate_transcript_update(payload: Any) -> dict[str, Any] | list[str]:
    if isinstance(payload, dict):
        mode = payload.get("mode", "replace")
        items = payload.get("items")
        if mode not in {"replace", "merge"}:
            raise UpdateChannelError("Transcript update mode must be replace or merge")
        if "items" not in payload:
            raise UpdateChannelError("Transcript update mode requires an items list")
        extra_keys = set(payload) - {"mode", "items"}
        if extra_keys:
            names = ", ".join(sorted(extra_keys))
            raise UpdateChannelError(f"Unsupported transcript update keys: {names}")
        return {"mode": mode, "items": _normalize_transcript_items(items)}

    return _normalize_transcript_items(payload)


def validate_update_payload(
    payload: Any, *, hud_schema: HudSchema | None = None
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise UpdateChannelError("Update payload must be an object")

    if not payload:
        raise UpdateChannelError("Update payload must not be empty")

    allowed_sections = {"hud", "content", "transcript"}
    extra_sections = set(payload) - allowed_sections
    if extra_sections:
        names = ", ".join(sorted(extra_sections))
        raise UpdateChannelError(f"Unsupported update sections: {names}")

    normalized: dict[str, Any] = {}
    if "hud" in payload:
        normalized["hud"] = _validate_hud_update(payload["hud"], hud_schema)
    if "content" in payload:
        normalized["content"] = _validate_content_update(payload["content"])
    if "transcript" in payload:
        normalized["transcript"] = _validate_transcript_update(payload["transcript"])
    return normalized


def extract_update(
    response: str, *, hud_schema: HudSchema | None = None
) -> dict[str, Any] | None:
    match = UPDATE_BLOCK_RE.search(response)
    if not match:
        return None
    payload = match.group("payload")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UpdateChannelError("Invalid CONTEXTGATE update payload") from exc
    return validate_update_payload(parsed, hud_schema=hud_schema)


def strip_update(response: str) -> str:
    stripped = UPDATE_BLOCK_RE.sub("", response)
    return stripped.strip()
