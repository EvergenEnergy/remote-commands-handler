"""Error handler module.


"""
import logging
import paho.mqtt.client as mqtt

from app.configuration import Configuration


class ErrorHandler:
    _client: mqtt.Client

    @classmethod
    def from_config(cls, config: Configuration):
        mqtt = config.get_mqtt_settings()
        if mqtt.pub_errors:
            return cls(mqtt.pub_errors, mqtt.error_topic, mqtt.port, mqtt.host)
        return cls(False, None, None, None)

    def __init__(self, active: bool, topic: str, port: int, host: str) -> None:
        self.active = active
        self.topic = topic
        self.host = host
        self.port = port
        self.client = None

    def publish(self, exception: Exception):
        if not self.active:
            return
        logging.info(f"Publishing an exception: {exception}")
