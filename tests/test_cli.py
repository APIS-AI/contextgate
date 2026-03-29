import json
from io import StringIO
from pathlib import Path

from contextgate.cli import main


def test_cli_normalizes_json_envelope(tmp_path, monkeypatch, capsys) -> None:
    envelope_path = tmp_path / "envelope.json"
    envelope_path.write_text(
        json.dumps(
            {
                "ctx_version": "0.1",
                "auth": {"source": "local_runtime", "trust": "trusted"},
                "hud_schema": {
                    "version": "v0",
                    "fields": {
                        "current_room_id": {"expected_type": "string"},
                    },
                },
                "hud": {"current_room_id": "room_123"},
            }
        )
    )

    assert main([str(envelope_path)]) == 0
    out = capsys.readouterr().out
    normalized = json.loads(out)
    assert normalized["hud"]["fields"]["current_room_id"] == "room_123"


def test_cli_normalizes_rendered_prompt_from_stdin(monkeypatch, capsys) -> None:
    rendered = """Prompt\n\n<CONTEXTGATE_ENVELOPE>\n{"ctx_version":"0.1","auth":{"source":"local_runtime","trust":"trusted"},"hud":{"fields":{"current_room_id":"room_123"},"mode":"replace"},"content":[],"transcript":[]}\n</CONTEXTGATE_ENVELOPE>"""
    monkeypatch.setattr("sys.stdin", StringIO(rendered))

    assert main([]) == 0
    out = capsys.readouterr().out
    normalized = json.loads(out)
    assert normalized["hud"]["fields"]["current_room_id"] == "room_123"
