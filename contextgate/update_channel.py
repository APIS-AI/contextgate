from __future__ import annotations

import json
import re
from typing import Any

UPDATE_BLOCK_RE = re.compile(
    r"<CONTEXTGATE_UPDATE>\s*(?P<payload>.*?)\s*</CONTEXTGATE_UPDATE>",
    re.DOTALL,
)


class UpdateChannelError(ValueError):
    pass


def _validate_hud_update(payload: Any) -> dict[str, Any]:
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
        return {"mode": mode, "fields": fields}

    if "mode" in payload:
        raise UpdateChannelError("HUD update mode requires a fields object")

    return payload


def validate_update_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise UpdateChannelError("Update payload must be an object")

    if not payload:
        raise UpdateChannelError("Update payload must not be empty")

    allowed_sections = {"hud"}
    extra_sections = set(payload) - allowed_sections
    if extra_sections:
        names = ", ".join(sorted(extra_sections))
        raise UpdateChannelError(f"Unsupported update sections: {names}")

    normalized: dict[str, Any] = {}
    if "hud" in payload:
        normalized["hud"] = _validate_hud_update(payload["hud"])
    return normalized


def extract_update(response: str) -> dict[str, Any] | None:
    match = UPDATE_BLOCK_RE.search(response)
    if not match:
        return None
    payload = match.group("payload")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UpdateChannelError("Invalid CONTEXTGATE update payload") from exc
    return validate_update_payload(parsed)


def strip_update(response: str) -> str:
    stripped = UPDATE_BLOCK_RE.sub("", response)
    return stripped.strip()
