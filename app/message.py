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
        except JSONDecodeError as ex:
            raise InvalidMessageError(f"Message is invalid JSON syntax: {ex}")

        if not message_obj.get("action") or "value" not in message_obj:
            raise InvalidMessageError(
                "Message is missing required components 'action' and/or 'value'"
            )
        return message_obj


class ErrorMessage:
    """Write an object in JSON format."""

    @classmethod
    def write(cls, message: dict):
        try:
            return json.dumps(message)
        except (TypeError, ValueError, OverflowError) as ex:
            logging.error(f"Couldn't write message {message}")
            raise InvalidMessageError(f"JSON object cannot be serialised: {ex}")
