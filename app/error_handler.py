"""Error handler module.


"""
import logging

from app.configuration import Configuration
from app.mqtt_writer import MqttWriter
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
            return cls(
                mqtt_settings.pub_errors,
                mqtt_settings.error_topic,
                mqtt_settings.host,
                mqtt_settings.port,
                mqtt_client,
            )
        return cls(False, None)

    def __init__(
        self,
        active: bool,
        topic: str = None,
        host: str = None,
        port: int = None,
        mqtt_client: mqtt.Client = None,
    ) -> None:
        self.active = active
        self.topic = topic
        self.host = host
        self.port = port

        if self.active:
            self.client = MqttWriter(self.port, self.host, mqtt_client)

    def publish(self, category: Category, message: str):
        logging.error(f"{category}: {message}")
        if not self.active or not self.client:
            return
        payload = {"category": category, "message": message}
        # TODO: look for device ID in environment var
        topic = f"{self.topic}/deviceid"
        logging.debug(f"Publishing a {category} error to topic {topic}: {message}")
        self.client.publish(topic, payload)
