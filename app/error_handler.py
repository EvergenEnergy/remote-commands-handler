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
            )
        return cls(False)

    def __init__(
        self,
        active: bool,
    ) -> None:
        self.active = active

    def publish(self, category: Category, message):
        logging.error(f"{category}: {message}")


class MQTTErrorHandler(ErrorHandler):
    def __init__(self, topic: str, host: str, port: int, client: mqtt.Client) -> None:
        super().__init__(True)
        self.topic = topic
        self.host = host
        self.port = port
        self.client = MqttWriter(self.host, self.port, client)

    def publish(self, category: ErrorHandler.Category, message: str):
        logging.error(f"{category}: {message}")
        payload = ErrorMessage.write({"category": category, "message": message})
        # TODO: look for device ID in environment var
        topic = f"{self.topic}/deviceid"
        logging.debug(f"Publishing a {category} error to topic {topic}: {message}")
        self.client.publish(topic, payload)
