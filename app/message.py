"""Message decoding and validation module.

This module encapsulates the functionality required to read and validate an incoming MQTT message.
"""

import json
from json import JSONDecodeError
import logging
from pydantic import validate_call, ValidationError

from app.exceptions import InvalidMessageError, UnknownCommandError
from app.configuration import Configuration, InputTypes


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
        MessageValidator.validate(self.input_type, self.value)

    def transform(self):
        #MessageValidator.validate(self.input_type, self.value)
        pass

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


class MessageValidator:
    @classmethod
    @validate_call
    def is_bool(cls, value: bool) -> bool:
        return True

    @classmethod
    def validate(cls, input_type, value):
        if input_type == InputTypes.COIL:
            try:
                cls.is_bool(value)
            except ValidationError:
                raise InvalidMessageError(
                    f"The {input_type.lower()} value {value!r} is invalid."
                )


class ErrorMessage:
    """Write an object in JSON format."""

    @classmethod
    def write(cls, message: dict):
        try:
            return json.dumps(message)
        except (TypeError, ValueError, OverflowError) as ex:
            logging.error(f"Couldn't write message {message}")
            raise InvalidMessageError(f"JSON object cannot be serialised: {ex}")
