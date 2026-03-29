from contextgate.update_channel import UpdateChannelError, extract_update, strip_update


def test_extract_update_reads_bounded_machine_channel() -> None:
    response = 'Visible text\n<CONTEXTGATE_UPDATE>{"hud":{"current_room_id":"room_123"}}</CONTEXTGATE_UPDATE>'
    assert extract_update(response) == {"hud": {"current_room_id": "room_123"}}


def test_strip_update_removes_machine_channel() -> None:
    response = 'Visible text\n<CONTEXTGATE_UPDATE>{"hud":{"current_room_id":"room_123"}}</CONTEXTGATE_UPDATE>'
    assert strip_update(response) == "Visible text"


def test_extract_update_rejects_invalid_json() -> None:
    response = 'Visible text\n<CONTEXTGATE_UPDATE>{not json}</CONTEXTGATE_UPDATE>'
    try:
        extract_update(response)
    except UpdateChannelError as exc:
        assert "Invalid CONTEXTGATE update payload" in str(exc)
    else:
        raise AssertionError("Expected UpdateChannelError")
