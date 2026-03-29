from __future__ import annotations

from contextgate.update_channel import UpdateChannelError, extract_update


EXAMPLES = {
    "accepted_hud_merge": """
<CONTEXTGATE_UPDATE>
{"hud":{"mode":"merge","fields":{"participant_count":5}}}
</CONTEXTGATE_UPDATE>
""".strip(),
    "accepted_content_merge": """
<CONTEXTGATE_UPDATE>
{"content":{"mode":"merge","items":[{"label":"room_title","field_class":"display_text","trust":"untrusted","value":"Main Room"}]}}
</CONTEXTGATE_UPDATE>
""".strip(),
    "accepted_transcript_merge": """
<CONTEXTGATE_UPDATE>
{"transcript":{"mode":"merge","items":["Older residue"]}}
</CONTEXTGATE_UPDATE>
""".strip(),
    "rejected_local_desktop": """
<CONTEXTGATE_UPDATE>
{"desktop":{"note":"local only"}}
</CONTEXTGATE_UPDATE>
""".strip(),
}


def main() -> None:
    for name, response in EXAMPLES.items():
        try:
            parsed = extract_update(response)
        except UpdateChannelError as exc:
            print(f"{name}: rejected -> {exc}")
            continue
        print(f"{name}: accepted -> {parsed}")


if __name__ == "__main__":
    main()
