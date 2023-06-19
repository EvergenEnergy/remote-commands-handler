"""Message decoding and validation module.

This module encapsulates the functionality required to read and validate an incoming MQTT message.
"""

from app.exceptions import InvalidMessageError
import json
from json import JSONDecodeError
import logging


class CommandMessage:
    """Read message contents and validate its structure."""

    @classmethod
    def read(cls, message_str: str):
        try:
            message_obj = json.loads(message_str)
            assert message_obj.get("action")
            assert "value" in message_obj
            return message_obj
        except JSONDecodeError as ex:
            raise InvalidMessageError(f"Message is invalid JSON syntax: {ex}")
        except AssertionError:
            raise InvalidMessageError(
                "Message is missing required components 'action' and/or 'value'"
            )
        except Exception as ex:
            raise InvalidMessageError(f"Invalid message: {ex}")


class ErrorMessage:
    """Write an object in JSON format."""

    @classmethod
    def write(cls, message: dict):
        try:
            return json.dumps(message)
        except Exception as ex:
            logging.error(f"Couldn't write message {message}")
            raise InvalidMessageError(f"JSON object cannot be serialised: {ex}")
