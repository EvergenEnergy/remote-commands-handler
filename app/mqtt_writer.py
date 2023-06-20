"""MQTT Writer module.

This module provides a client class for publishing messages to MQTT brokers.

"""

import logging

import paho.mqtt.client as mqtt

from app.message import ErrorMessage
from app.mqtt_client import MqttClient


class MqttWriter(MqttClient):
    _client: mqtt.Client

    def __init__(
        self,
        port: int,
        host: str,
        client: mqtt.Client = None,
    ) -> None:
        super().__init__(host, port, client)
        self._client.on_publish = self._on_publish()

    def publish(self, topic, payload):
        if self.connect():
            self._client.publish(topic, ErrorMessage.write(payload), qos=1)
            return
        logging.error(f"Failed to publish to {topic}: {payload}")

    def _on_publish(self):
        def inner(_client, _userdata, message_id):
            logging.debug(f"Published message with id {message_id}")

        return inner
