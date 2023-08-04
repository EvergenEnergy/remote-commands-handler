"""Message decoding and validation module.

This module encapsulates the functionality required to read and validate an incoming MQTT message.
"""

import json
from json import JSONDecodeError
import logging

from app.exceptions import InvalidMessageError, UnknownCommandError
from app.configuration import Configuration


class CommandMessage:
    """Create a CommandMessage object and retrieve its configuration."""

    def __init__(self, name: str, value, configuration: Configuration) -> None:
        self.name = name
        self.value = value
        self.configuration = configuration.get_coil(
            self.name
        ) or configuration.get_holding_register(self.name)
        if self.configuration:
            self.input_type = self.configuration.input_type
        else:
            raise UnknownCommandError(self.name)

    def validate(self):
        logging.info(f"input config for {self.name}: {self.configuration}")
        is_valid = True
        if not is_valid:
            raise InvalidMessageError("Message wasn't valid")
        return True

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
