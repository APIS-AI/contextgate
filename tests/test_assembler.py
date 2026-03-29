from contextgate.assembler import assemble_hud
from contextgate.schemas import FieldSpec, HudSchema, ValidationError


def test_assemble_hud_validates_known_fields() -> None:
    schema = HudSchema(
        version="v0",
        fields={
            "current_room_id": FieldSpec(expected_type="string"),
            "participant_count": FieldSpec(expected_type="integer"),
        },
    )

    hud = assemble_hud(
        {"current_room_id": "room_123", "participant_count": 3},
        schema,
    )

    assert hud == {
        "mode": "replace",
        "fields": {"current_room_id": "room_123", "participant_count": 3},
    }


def test_assemble_hud_rejects_invalid_type() -> None:
    schema = HudSchema(
        version="v0",
        fields={"participant_count": FieldSpec(expected_type="integer")},
    )

    try:
        assemble_hud({"participant_count": "three"}, schema, on_unknown="reject")
    except ValidationError as exc:
        assert "Expected integer" in str(exc)
    else:
        raise AssertionError("Expected ValidationError")


def test_assemble_hud_validates_typed_arrays() -> None:
    schema = HudSchema(version="v0", fields={"room_ids": FieldSpec(expected_type="string[]")})

    hud = assemble_hud({"room_ids": ["room_123", "room_456"]}, schema)

    assert hud["fields"]["room_ids"] == ["room_123", "room_456"]


def test_assemble_hud_rejects_invalid_timestamp() -> None:
    schema = HudSchema(version="v0", fields={"last_event_at": FieldSpec(expected_type="timestamp")})

    try:
        assemble_hud({"last_event_at": "not-a-timestamp"}, schema)
    except ValidationError as exc:
        assert "timestamp" in str(exc).lower()
    else:
        raise AssertionError("Expected ValidationError")


def test_assemble_hud_validates_schema_bound_image_ref() -> None:
    schema = HudSchema(
        version="v0",
        fields={"current_screenshot": FieldSpec(expected_schema="ImageRefV1")},
    )

    hud = assemble_hud(
        {
            "current_screenshot": {
                "uri": "file:///tmp/screenshot.png",
                "mime_type": "image/png",
                "sha256": "abc123",
                "width": 1440,
                "height": 900,
            }
        },
        schema,
    )

    assert hud["fields"]["current_screenshot"]["mime_type"] == "image/png"


def test_assemble_hud_rejects_invalid_audio_ref() -> None:
    schema = HudSchema(
        version="v0",
        fields={"recent_voice_note": FieldSpec(expected_schema="AudioRefV1")},
    )

    try:
        assemble_hud(
            {
                "recent_voice_note": {
                    "uri": "file:///tmp/note.wav",
                    "mime_type": "audio/wav",
                    "sha256": "abc123",
                }
            },
            schema,
        )
    except ValidationError as exc:
        assert "duration_ms" in str(exc)
    else:
        raise AssertionError("Expected ValidationError")


def test_assemble_hud_validates_schema_bound_image_ref_list() -> None:
    schema = HudSchema(
        version="v0",
        fields={"recent_screenshots": FieldSpec(expected_schema="ImageRefV1[]")},
    )

    hud = assemble_hud(
        {
            "recent_screenshots": [
                {
                    "uri": "file:///tmp/one.png",
                    "mime_type": "image/png",
                    "sha256": "abc123",
                },
                {
                    "uri": "file:///tmp/two.png",
                    "mime_type": "image/png",
                    "sha256": "def456",
                },
            ]
        },
        schema,
    )

    assert len(hud["fields"]["recent_screenshots"]) == 2
