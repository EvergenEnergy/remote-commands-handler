"""Tests for the CommandMessage and ErrorMessage modules."""

import pytest
from datetime import datetime
import json
from app.configuration import Configuration
from app.message import CommandMessage, ErrorMessage
from app.exceptions import InvalidMessageError, UnknownCommandError


class TestCommandMessage:
    def setup_method(self):
        self.configuration = Configuration.from_file(
            "tests/config/example_configuration.yaml"
        )

    def test_good_cmd_message(self):
        json_obj = {"action": "somecoil", "value": True}
        json_str = json.dumps(json_obj)
        read_msg = CommandMessage.read(json_str)
        assert "action" in read_msg
        assert "value" in read_msg

    def test_unknown_command(self):
        with pytest.raises(UnknownCommandError) as ex:
            CommandMessage("bad_register", 54, self.configuration)
        assert "No coil or register found to match 'bad_register'" in str(ex)
        with pytest.raises(UnknownCommandError) as ex:
            CommandMessage("", False, self.configuration)
        assert "No coil or register found" in str(ex)

    def test_bad_cmd_message_structure(self):
        json_obj = {"action": "somecoil", "value": True}
        for key in ("action", "value"):
            json_obj["foo"] = json_obj[key]
            del json_obj[key]
            json_str = json.dumps(json_obj)
            with pytest.raises(InvalidMessageError) as ex:
                _ = CommandMessage.read(json_str)
            assert "Message is missing required components" in str(ex.value)
            assert ex.type == InvalidMessageError
            json_obj[key] = json_obj["foo"]

    def test_bad_cmd_message_syntax(self):
        json_str = "not a real json string"
        with pytest.raises(InvalidMessageError) as ex:
            _ = CommandMessage.read(json_str)
        assert "Message is invalid JSON syntax" in str(ex.value)
        assert ex.type == InvalidMessageError

    def test_bad_cmd_message_datatype(self):
        msg = CommandMessage("evgBatteryModeCoil", True, self.configuration)
        assert msg.validate() is True
        msg = CommandMessage("evgBatteryModeCoil", "foo", self.configuration)
        with pytest.raises(InvalidMessageError) as ex:
            msg.validate()
        assert "The coil value 'foo' is invalid" in str(ex.value)
        assert ex.type == InvalidMessageError


class TestErrorMessage:
    def test_good_err_message(self):
        json_obj = {"category": "RuntimeError", "message": "oops"}
        json_str = ErrorMessage.write(json_obj)
        assert json_str == """{"category": "RuntimeError", "message": "oops"}"""

    def test_bad_err_message(self):
        json_obj = {
            "category": "RuntimeError",
            "message": "something went wrong",
            "timestamp": datetime.now(),
        }
        with pytest.raises(InvalidMessageError) as ex:
            _ = ErrorMessage.write(json_obj)
        assert "serialised" in str(ex)
