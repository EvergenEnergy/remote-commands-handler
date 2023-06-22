"""MQTT Reader module.

This module provides a client class for subscribing to topics and receiving messages from MQTT brokers.

"""

import logging
from typing import Callable

import paho.mqtt.client as mqtt

from app.message import CommandMessage
from app.exceptions import InvalidMessageError
from app.error_handler import ErrorHandler


def _decode_message(message):
    return message.payload.decode()


class MqttReader:
    def __init__(
        self,
        host: str,
        port: int,
        topics: list[str],
        client: mqtt.Client,
        error_handler: ErrorHandler,
    ) -> None:
        self.host = host
        self.port = port
        self.error_handler = error_handler
        self._on_message_callbacks = []
        self._topics = topics
        self._client = client

    def add_message_callback(self, f: Callable[[str], None]):
        self._on_message_callbacks.append(f)

    def connect(self) -> None:
        try:
            self._client.connect(self.host, self.port)
            return True
        except OSError as e:
            ex = OSError(f"Cannot connect to MQTT broker at {self.host}:{self.port}")
            raise ex from e

    def stop(self) -> None:
        self._client.disconnect()

    def run(self) -> None:
        """Run the MQTT client.

        This method blocks the execution and keeps the client connected to the MQTT broker.
        """
        self._client.on_connect = self._on_connect()
        self._client.on_disconnect = self._on_disconnect()
        self._client.on_message = self._on_message()

        self.connect()

        logging.info("Service started")
        self._client.loop_forever()

    def _on_message(self):
        def inner(_client, _userdata, message):
            try:
                msg_str = _decode_message(message)
                msg_obj = CommandMessage.read(msg_str)
            except InvalidMessageError as ex:
                self.error_handler.publish(
                    self.error_handler.Category.INVALID_MESSAGE, str(ex)
                )
                return
            for callback in self._on_message_callbacks:
                callback(msg_obj)

        return inner

    def _on_connect(self):
        def inner(client, _userdata, _flags, rc):
            if rc == 0:
                logging.info("Connected to MQTT broker")
                for topic in self._topics:
                    logging.info("Subscribing to topic: %s", topic)
                    client.subscribe(topic)
            else:
                logging.error("Connection failed")

        return inner

    def _on_disconnect(self):
        def inner(client, _userdata, rc):
            if rc > 0:
                logging.error(f"MQTT client has disconnected: {rc}")

        return inner
