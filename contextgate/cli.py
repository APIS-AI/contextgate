from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .gate import ContextGate
from .parser import parse_envelope
from .schemas import parse_hud_schema
from .update_channel import extract_update, strip_update


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
    parser.add_argument(
        "--write-state",
        help="Optional path to write the resulting normalized envelope JSON.",
    )
    parser.add_argument(
        "--compact-json",
        action="store_true",
        help="Print compact JSON instead of indented JSON when not using --render.",
    )
    parser.add_argument(
        "--read-update-from-field",
        help="Optional dot path to a string field inside a JSON input object used as model output text.",
    )
    parser.add_argument(
        "--stdout",
        choices=("json", "render", "visible-text"),
        help="Override stdout behavior. Useful with --write-state when machine state and visible text need to be split.",
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


def load_json_payload(raw_text: str) -> dict[str, Any]:
    payload = json.loads(raw_text)
    if not isinstance(payload, dict):
        raise ValueError("Expected top-level JSON object when reading from a field")
    return payload


def read_string_field(payload: dict[str, Any], field_path: str) -> str:
    current: Any = payload
    for part in field_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"Missing field path: {field_path}")
        current = current[part]
    if not isinstance(current, str):
        raise ValueError(f"Field path must resolve to a string: {field_path}")
    return current


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


def write_state(path: str, envelope: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")


def resolve_stdout_mode(args: argparse.Namespace) -> str:
    if args.stdout:
        return args.stdout
    if args.render:
        return "render"
    return "json"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_text = load_text(args.input)
    default_schema = load_schema(args.schema)
    visible_text: str | None = None

    if args.read_update_from_field:
        try:
            payload = load_json_payload(raw_text)
            raw_text = read_string_field(payload, args.read_update_from_field)
        except Exception as exc:
            print(f"contextgate: {exc}", file=sys.stderr)
            return 1

    try:
        if args.apply_update:
            gate = build_gate(args, default_schema)
            if args.state:
                load_initial_state(args.state, gate)
            visible_text = strip_update(raw_text)
            normalized = gate.extract_update(raw_text)
            if normalized is None:
                raise ValueError("No CONTEXTGATE update block found")
            gate.apply_update(normalized)
            normalized = gate.build_envelope()
        elif args.update:
            visible_text = strip_update(raw_text)
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

    if args.write_state and isinstance(normalized, dict):
        write_state(args.write_state, normalized)

    stdout_mode = resolve_stdout_mode(args)
    if stdout_mode == "visible-text":
        if visible_text is None:
            print("contextgate: --stdout visible-text requires --update or --apply-update", file=sys.stderr)
            return 1
        print(visible_text)
    elif stdout_mode == "render":
        if not isinstance(normalized, dict) or "ctx_version" not in normalized:
            print("contextgate: render output requires a normalized envelope", file=sys.stderr)
            return 1
        print(render_envelope_block(normalized, base_prompt=args.base_prompt))
    else:
        if args.compact_json:
            print(json.dumps(normalized, separators=(",", ":"), sort_keys=True))
        else:
            print(json.dumps(normalized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
