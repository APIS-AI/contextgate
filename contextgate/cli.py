from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .parser import parse_envelope
from .schemas import parse_hud_schema
from .update_channel import extract_update


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="contextgate")
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Path to a JSON envelope or a rendered prompt block. Use - for stdin.",
    )
    parser.add_argument(
        "--schema",
        help="Optional path to a HUD schema JSON file used as the default schema.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Parse only the CONTEXTGATE update channel from model output.",
    )
    return parser


def load_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text()


def load_schema(path: str | None):
    if not path:
        return None
    payload = json.loads(Path(path).read_text())
    return parse_hud_schema(payload)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_text = load_text(args.input)
    default_schema = load_schema(args.schema)

    try:
        if args.update:
            normalized = extract_update(raw_text, hud_schema=default_schema)
            if normalized is None:
                raise ValueError("No CONTEXTGATE update block found")
        else:
            try:
                payload: dict[str, Any] | str = json.loads(raw_text)
            except json.JSONDecodeError:
                payload = raw_text
            normalized = parse_envelope(payload, default_hud_schema=default_schema)
    except Exception as exc:
        print(f"contextgate: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(normalized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
