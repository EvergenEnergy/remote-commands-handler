"""MQTT Writer module.

This module provides a client class for publishing messages to MQTT brokers.

"""

import logging

import paho.mqtt.client as mqtt


class MqttWriter:
    _client: mqtt.Client

    def __init__(self, host: str, port: int, client: mqtt.Client) -> None:
        self.host = host
        self.port = port
        self._client = client

    def connect(self) -> None:
        try:
            self._client.connect(self.host, self.port)
            return True
        except OSError as e:
            ex = OSError(f"Cannot connect to MQTT broker at {self.host}:{self.port}")
            raise ex from e

    def publish(self, topic: str, payload: str):
        if self.connect():
            response = self._client.publish(topic, payload, qos=1)
            if response[0] == 0:
                logging.debug(f"Published message successfully with id {response[1]}")
                return
        logging.error(f"Failed to publish to {topic}: {payload}")
