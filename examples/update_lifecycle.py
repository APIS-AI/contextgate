from __future__ import annotations

import sys
from pathlib import Path

from contextgate import ContextGate

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.trusted_hud_from_os import build_trusted_os_hud


def main() -> None:
    hud_schema, trusted_hud = build_trusted_os_hud()

    gate = ContextGate(default_hud_schema=hud_schema)
    gate.register_hud_schema(hud_schema)
    gate.assemble_hud(trusted_hud)
    gate.apply_update(
        {
            "content": [
                {
                    "label": "room_title",
                    "field_class": "display_text",
                    "trust": "untrusted",
                    "value": "Main Room",
                }
            ],
            "transcript": ["Older residue"],
        }
    )

    initial_prompt = gate.render(
        base_prompt="Summarize the room state and propose the next action.",
        compact=True,
    )

    response = """
Summary: The room is stable.
<CONTEXTGATE_UPDATE>
{"hud":{"mode":"merge","fields":{"current_date_local":"2026-03-28"}},"content":{"mode":"merge","items":[{"label":"latest_message","field_class":"message_text","trust":"untrusted","value":"Hello from the room"}]},"transcript":{"mode":"merge","items":["Model summarized the room."]}}
</CONTEXTGATE_UPDATE>
""".strip()

    update = gate.extract_update(response)
    gate.apply_update(update)
    rerendered_prompt = gate.render(
        base_prompt="Continue with the updated room state.",
        compact=True,
    )

    print("INITIAL")
    print(initial_prompt)
    print()
    print("VISIBLE RESPONSE")
    print(gate.visible_text(response))
    print()
    print("RERENDERED")
    print(rerendered_prompt)


if __name__ == "__main__":
    main()
