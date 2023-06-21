"""Error handler module.


"""
import logging

from app.configuration import Configuration
from app.mqtt_writer import MqttWriter
from app.exceptions import InvalidArgumentError
from app.message import ErrorMessage
import paho.mqtt.client as mqtt


class ErrorHandler:
    class Category:
        MODBUS_ERROR = "ModbusError"
        MQTT_ERROR = "MQTTError"
        INVALID_MESSAGE = "InvalidMessage"
        UNKNOWN_COMMAND = "UnknownCommand"

    @classmethod
    def from_config(cls, config: Configuration, mqtt_client: mqtt.Client = None):
        mqtt_settings = config.get_mqtt_settings()
        if mqtt_settings.pub_errors:
            if not mqtt_client:
                raise InvalidArgumentError(
                    "ErrorHandler requires MQTT settings and client when enabled"
                )
            return MQTTErrorHandler(
                mqtt_settings.error_topic,
                mqtt_settings.host,
                mqtt_settings.port,
                mqtt_client,
                config.get_env().site_name,
                config.get_env().serial_number,
            )
        return cls(False, config.get_env().site_name, config.get_env().serial_number)

    def __init__(
        self,
        active: bool,
        site_name: str,
        serial_number: str,
    ) -> None:
        self.active = active
        self.site_name = site_name
        self.serial_number = serial_number

    def publish(self, category: Category, message):
        logging.error(f"{category}: {message}")


class MQTTErrorHandler(ErrorHandler):
    def __init__(
        self,
        topic: str,
        host: str,
        port: int,
        client: mqtt.Client,
        site_name: str,
        serial_number: str,
    ) -> None:
        super().__init__(True, site_name, serial_number)
        self.topic = topic
        self.host = host
        self.port = port
        self.client = MqttWriter(self.host, self.port, client)

    def publish(self, category: ErrorHandler.Category, message: str):
        logging.error(f"{category}: {message}")
        payload = ErrorMessage.write({"category": category, "message": message})
        topic = f"{self.topic}/{self.site_name}/{self.serial_number}"
        logging.debug(f"Publishing a {category} error to topic {topic!r}: {message}")
        self.client.publish(topic, payload)
