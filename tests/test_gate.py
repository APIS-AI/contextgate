import json

from contextgate.gate import ContextGate


def test_render_emits_structured_envelope_block() -> None:
    gate = ContextGate()
    rendered = gate.render(
        base_prompt="Summarize the room state.",
        hud={"mode": "replace", "fields": {"current_room_id": "room_123"}},
        content=[{"label": "room_title", "trust": "untrusted", "value": "Main Room"}],
        transcript=["Older residue"],
    )

    assert "<CONTEXTGATE_ENVELOPE>" in rendered
    assert "</CONTEXTGATE_ENVELOPE>" in rendered

    payload = rendered.split("<CONTEXTGATE_ENVELOPE>\n", 1)[1].split("\n</CONTEXTGATE_ENVELOPE>", 1)[0]
    envelope = json.loads(payload)

    assert envelope["ctx_version"] == "0.1"
    assert envelope["auth"] == {"source": "local_runtime", "trust": "trusted"}
    assert envelope["hud"]["fields"]["current_room_id"] == "room_123"


def test_render_supports_compact_mode() -> None:
    gate = ContextGate()
    rendered = gate.render(
        base_prompt="Summarize the room state.",
        hud={"mode": "replace", "fields": {"current_room_id": "room_123"}},
        compact=True,
    )

    payload = rendered.split("<CONTEXTGATE_ENVELOPE>\n", 1)[1].split("\n</CONTEXTGATE_ENVELOPE>", 1)[0]
    assert "\n" not in payload
    envelope = json.loads(payload)
    assert envelope["hud"]["fields"]["current_room_id"] == "room_123"


def test_apply_update_supports_merge_mode() -> None:
    gate = ContextGate(
        default_hud_schema={
            "version": "v0",
            "fields": {
                "current_room_id": {"expected_type": "string"},
                "participant_count": {"expected_type": "integer"},
            },
        }
    )
    gate.assemble_hud({"current_room_id": "room_123", "participant_count": 4})

    gate.apply_update({"hud": {"mode": "merge", "fields": {"participant_count": 5}}})

    assert gate.active_hud == {
        "mode": "replace",
        "fields": {"current_room_id": "room_123", "participant_count": 5},
    }
