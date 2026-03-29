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


def extract_update(response: str) -> dict[str, Any] | None:
    match = UPDATE_BLOCK_RE.search(response)
    if not match:
        return None
    payload = match.group("payload")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UpdateChannelError("Invalid CONTEXTGATE update payload") from exc
    if not isinstance(parsed, dict):
        raise UpdateChannelError("Update payload must be an object")
    return parsed


def strip_update(response: str) -> str:
    stripped = UPDATE_BLOCK_RE.sub("", response)
    return stripped.strip()
