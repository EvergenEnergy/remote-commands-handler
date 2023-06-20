"""MQTT Reader module.

This module provides a client class for subscribing to topics and receiving messages from MQTT brokers.

"""

import logging
from typing import Callable

import paho.mqtt.client as mqtt

from app.message import CommandMessage
from app.exceptions import InvalidMessageError
from app.error_handler import ErrorHandler
from app.mqtt_client import MqttClient


def _decode_message(message):
    return message.payload.decode()


class MqttReader(MqttClient):
    _client: mqtt.Client

    def __init__(
        self,
        port: int,
        host: str,
        error_handler: ErrorHandler,
        client: mqtt.Client = None,
    ) -> None:
        super().__init__(host, port, client)
        self.error_handler = error_handler
        self.on_message_callbacks = []
        self.topics = []

    def subscribe_topics(self, topics: list[str]):
        for topic in topics:
            self.topics.append(topic)

    def add_message_callback(self, f: Callable[[str], None]):
        self.on_message_callbacks.append(f)

    def stop(self) -> None:
        self._client.disconnect()

    def run(self) -> None:
        """Run the MQTT client.

        This method blocks the execution and keeps the client connected to the MQTT broker.
        """
        self._client.on_connect = self._on_connect()
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
                logging.error(ex)
                self.error_handler.publish(
                    self.error_handler.Category.INVALID_MESSAGE, str(ex)
                )
                return
            for callback in self.on_message_callbacks:
                callback(msg_obj)

        return inner

    def _on_connect(self):
        def inner(client, _userdata, _flags, rc):
            if rc == 0:
                logging.info("Connected to MQTT broker")
                for topic in self.topics:
                    logging.info("Subscribing to topic: %s", topic)
                    client.subscribe(topic)
            else:
                logging.error("Connection failed")

        return inner
