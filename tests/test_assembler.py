from contextgate.assembler import assemble_hud
from contextgate.schemas import FieldSpec, HudSchema, ValidationError


def test_assemble_hud_validates_known_fields() -> None:
    schema = HudSchema(
        version="v0",
        fields={
            "current_room_id": FieldSpec("string"),
            "participant_count": FieldSpec("integer"),
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
    schema = HudSchema(version="v0", fields={"participant_count": FieldSpec("integer")})

    try:
        assemble_hud({"participant_count": "three"}, schema, on_unknown="reject")
    except ValidationError as exc:
        assert "Expected integer" in str(exc)
    else:
        raise AssertionError("Expected ValidationError")


def test_assemble_hud_validates_typed_arrays() -> None:
    schema = HudSchema(version="v0", fields={"room_ids": FieldSpec("string[]")})

    hud = assemble_hud({"room_ids": ["room_123", "room_456"]}, schema)

    assert hud["fields"]["room_ids"] == ["room_123", "room_456"]


def test_assemble_hud_rejects_invalid_timestamp() -> None:
    schema = HudSchema(version="v0", fields={"last_event_at": FieldSpec("timestamp")})

    try:
        assemble_hud({"last_event_at": "not-a-timestamp"}, schema)
    except ValidationError as exc:
        assert "timestamp" in str(exc).lower()
    else:
        raise AssertionError("Expected ValidationError")
