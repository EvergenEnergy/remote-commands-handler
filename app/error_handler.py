"""Error handler module.


"""
import time
import logging

from app.configuration import Configuration
from app.mqtt_writer import MqttWriter
from app.message import ErrorMessage
import paho.mqtt.client as mqtt


class ErrorHandler:
    _client: mqtt.Client

    class Category:
        MODBUS_ERROR = "ModbusError"
        MQTT_ERROR = "MQTTError"
        INVALID_MESSAGE = "InvalidMessage"
        UNKNOWN_COMMAND = "UnknownCommand"
        UNHANDLED = "UnhandledException"

    def __init__(self, config: Configuration, mqtt_client: mqtt.Client):
        mqtt_settings = config.get_mqtt_settings()
        if not mqtt_settings.pub_errors:
            self.active = False
            self.host = None
            self.port = None
            self.topic = None
            self._client = None
            return

        self.active = True
        self.host = mqtt_settings.host
        self.port = mqtt_settings.port
        self.topic = mqtt_settings.error_topic
        self._client = MqttWriter(self.host, self.port, mqtt_client)

    def publish(self, category: Category, message: str):
        logging.error(f"{category}: {message}")
        if not self.active:
            return
        payload = ErrorMessage.write(
            {"category": category, "message": message, "timestamp": time.time()}
        )
        topic = f"{self.topic}/{category}"
        logging.info(f"Publishing a {category} error to topic {topic}: {message}")
        self._client.publish(topic, payload)
