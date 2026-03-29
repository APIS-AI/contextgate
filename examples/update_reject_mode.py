from __future__ import annotations

from contextgate import ContextGate


def main() -> None:
    gate = ContextGate(content_limit=1, content_overflow="reject")
    gate.apply_update(
        {
            "content": [
                {
                    "label": "room_title",
                    "field_class": "display_text",
                    "trust": "untrusted",
                    "value": "Main Room",
                }
            ]
        }
    )

    response = """
Summary: The room has new activity.
<CONTEXTGATE_UPDATE>
{"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello"}]}}
</CONTEXTGATE_UPDATE>
""".strip()

    try:
        update = gate.extract_update(response)
        gate.apply_update(update)
    except ValueError as exc:
        print(f"Rejected update: {exc}")
        return

    print("Update unexpectedly succeeded")


if __name__ == "__main__":
    main()
