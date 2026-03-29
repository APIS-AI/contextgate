from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .gate import ContextGate
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
    parser.add_argument(
        "--apply-update",
        action="store_true",
        help="Extract an update, apply it to active state, and print the resulting envelope.",
    )
    parser.add_argument(
        "--state",
        help="Optional path to an initial envelope JSON file or rendered prompt block.",
    )
    parser.add_argument(
        "--content-limit",
        type=int,
        help="Maximum number of active content items after policy application.",
    )
    parser.add_argument(
        "--transcript-limit",
        type=int,
        help="Maximum number of active transcript items after policy application.",
    )
    parser.add_argument(
        "--dedupe-content",
        action="store_true",
        help="Remove repeated content items before applying content limits.",
    )
    parser.add_argument(
        "--dedupe-transcript",
        action="store_true",
        help="Remove repeated transcript items before applying transcript limits.",
    )
    parser.add_argument(
        "--content-overflow",
        choices=("truncate", "reject"),
        default="truncate",
        help="Behavior when content exceeds --content-limit after policy application.",
    )
    parser.add_argument(
        "--transcript-overflow",
        choices=("truncate", "reject"),
        default="truncate",
        help="Behavior when transcript exceeds --transcript-limit after policy application.",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Print the resulting envelope as a CONTEXTGATE_ENVELOPE block instead of JSON.",
    )
    parser.add_argument(
        "--base-prompt",
        default="",
        help="Optional prompt prefix used with --render.",
    )
    parser.add_argument(
        "--report-sizes",
        action="store_true",
        help="Print active state sizes to stderr after successful normalization or apply.",
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


def build_gate(args: argparse.Namespace, default_schema: Any) -> ContextGate:
    return ContextGate(
        default_hud_schema=default_schema,
        content_limit=args.content_limit,
        transcript_limit=args.transcript_limit,
        dedupe_content=args.dedupe_content,
        dedupe_transcript=args.dedupe_transcript,
        content_overflow=args.content_overflow,
        transcript_overflow=args.transcript_overflow,
    )


def load_initial_state(path: str, gate: ContextGate) -> None:
    raw_text = load_text(path)
    try:
        payload: dict[str, Any] | str = json.loads(raw_text)
    except json.JSONDecodeError:
        payload = raw_text
    normalized = gate.parse_envelope(payload)
    gate.active_hud = dict(normalized["hud"])
    gate.active_content = list(normalized["content"])
    gate.active_transcript = list(normalized["transcript"])


def render_envelope_block(
    envelope: dict[str, Any], *, base_prompt: str = "", compact: bool = True
) -> str:
    json_kwargs = {"sort_keys": True}
    if compact:
        payload = json.dumps(envelope, separators=(",", ":"), **json_kwargs)
    else:
        payload = json.dumps(envelope, indent=2, **json_kwargs)
    lines: list[str] = []
    if base_prompt:
        lines.extend([base_prompt.rstrip(), ""])
    lines.extend(["<CONTEXTGATE_ENVELOPE>", payload, "</CONTEXTGATE_ENVELOPE>"])
    return "\n".join(lines)


def emit_size_report(envelope: dict[str, Any]) -> None:
    hud = envelope.get("hud", {})
    hud_fields = 0
    if isinstance(hud, dict):
        fields = hud.get("fields", {})
        if isinstance(fields, dict):
            hud_fields = len(fields)
    content = envelope.get("content", [])
    transcript = envelope.get("transcript", [])
    print(
        "contextgate: size "
        f"hud_fields={hud_fields} "
        f"content_items={len(content)} "
        f"transcript_items={len(transcript)}",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_text = load_text(args.input)
    default_schema = load_schema(args.schema)

    try:
        if args.apply_update:
            gate = build_gate(args, default_schema)
            if args.state:
                load_initial_state(args.state, gate)
            normalized = gate.extract_update(raw_text)
            if normalized is None:
                raise ValueError("No CONTEXTGATE update block found")
            gate.apply_update(normalized)
            normalized = gate.build_envelope()
        elif args.update:
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

    if args.report_sizes and isinstance(normalized, dict):
        emit_size_report(normalized)

    if args.render:
        print(render_envelope_block(normalized, base_prompt=args.base_prompt))
    else:
        print(json.dumps(normalized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
