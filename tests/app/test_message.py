"""Tests for the CommandMessage and ErrorMessage modules."""

import pytest
import json
from app.message import CommandMessage, ErrorMessage
from app.exceptions import InvalidMessageError


def test_good_cmd_message():
    json_obj = {"action": "somecoil", "value": True}
    json_str = json.dumps(json_obj)
    read_msg = CommandMessage.read(json_str)
    assert "action" in read_msg
    assert "value" in read_msg


def test_bad_cmd_message_structure():
    json_obj = {"action": "somecoil", "value": True}
    for key in ("action", "value"):
        json_obj["foo"] = json_obj[key]
        del json_obj[key]
        json_str = json.dumps(json_obj)
        print(json_str)
        with pytest.raises(InvalidMessageError) as ex:
            _ = CommandMessage.read(json_str)
        assert "Message is missing required components" in str(ex.value)
        assert ex.type == InvalidMessageError
        json_obj[key] = json_obj["foo"]


def test_bad_cmd_message_syntax():
    json_str = "not a real json string"
    with pytest.raises(InvalidMessageError) as ex:
        _ = CommandMessage.read(json_str)
    assert "Message is invalid JSON syntax" in str(ex.value)
    assert ex.type == InvalidMessageError


def test_bad_cmd_message_unhandled_exception(monkeypatch):
    def fake_json_load(_):
        raise TypeError("unpredictable error")

    with monkeypatch.context() as m:
        m.setattr(
            json,
            "loads",
            fake_json_load,
        )
        with pytest.raises(InvalidMessageError) as ex:
            _ = CommandMessage.read("")
        assert "Invalid message" in str(ex.value)
        assert ex.type == InvalidMessageError
