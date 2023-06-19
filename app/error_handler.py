"""Error handler module.


"""
import logging

from app.configuration import Configuration


class ErrorHandler:
    class Category:
        MODBUS_ERROR = "ModbusError"
        MQTT_ERROR = "MQTTError"
        INVALID_MESSAGE = "InvalidMessage"
        UNKNOWN_COMMAND = "UnknownCommand"
        RUNTIME_ERROR = "RuntimeError"

    @classmethod
    def from_config(cls, config: Configuration):
        mqtt = config.get_mqtt_settings()
        if mqtt.pub_errors:
            return cls(mqtt.pub_errors, mqtt.error_topic)
        return cls(False, None)

    def __init__(self, active: bool, topic: str) -> None:
        self.active = active
        self.topic = topic
        self.client = None

    def publish(self, category: Category, message: str):
        if not self.active or not self.client:
            return
        payload = {"category": category, "message": message}
        # TODO: look for device ID in environment var
        topic = f"{self.topic}/deviceid"
        logging.debug(f"Publishing a {category} error to topic {topic}: {message}")
        self.client.publish(topic, payload)
