from contextgate import ContextGate


def main() -> None:
    gate = ContextGate(
        default_hud_schema={
            "version": "v0",
            "fields": {
                "current_room_id": {"expected_type": "string"},
                "participant_count": {"expected_type": "integer"},
                "last_event_at": {"expected_type": "timestamp"},
            },
        }
    )

    gate.register_hud_schema(
        {
            "version": "v0",
            "fields": {
                "current_room_id": {"expected_type": "string"},
                "participant_count": {"expected_type": "integer"},
                "last_event_at": {"expected_type": "timestamp"},
            },
        }
    )

    hud = gate.assemble_hud(
        {
            "current_room_id": "room_123",
            "participant_count": 4,
            "last_event_at": "2026-03-28T15:00:00Z",
        }
    )

    prompt = gate.render(
        base_prompt="Summarize the room state.",
        hud=hud,
        content=[{"label": "room_title", "trust": "untrusted", "value": "Main Room"}],
        transcript=["Previous turn summary."],
    )

    response = (
        "Room room_123 has 4 participants.\n"
        "<CONTEXTGATE_UPDATE>{\"hud\":{\"participant_count\":5}}</CONTEXTGATE_UPDATE>"
    )

    update = gate.extract_update(response)
    gate.apply_update(update)

    print(prompt)
    print()
    print(gate.visible_text(response))
    print(gate.active_hud)


if __name__ == "__main__":
    main()
