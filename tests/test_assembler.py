from contextgate.assembler import assemble_hud
from contextgate.schemas import HudSchema, FieldSpec, ValidationError


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
