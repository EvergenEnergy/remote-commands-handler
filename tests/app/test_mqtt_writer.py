"""Unit tests for the MqttWriter class in the app.mqtt_writer module."""

from unittest.mock import MagicMock
import paho.mqtt.client as mqtt
from app.mqtt_writer import MqttWriter
import pytest
import json


class TestMqttWriter:
    def setup_method(self):
        self.mock_mqtt_client = MagicMock(spec=mqtt.Client)
        self.mqtt_writer = MqttWriter(
            host="localhost",
            port=1883,
            client=self.mock_mqtt_client,
        )
        self.topic = "/some/topic"
        self.payload = {"category": "SomeError", "message": "Things went wrong"}
        self.payload_str = json.dumps(self.payload)

    def test_create(self):
        assert self.mqtt_writer.port == 1883

    def test_publish(self):
        self.mock_mqtt_client.connect.return_value = 0
        self.mock_mqtt_client.publish.return_value = (0, 1)

        self.mqtt_writer.publish(self.topic, self.payload_str)

        # Verify that client methods were called with the correct parameters
        self.mock_mqtt_client.connect.assert_called_with("localhost", 1883)
        self.mock_mqtt_client.publish.assert_called_with(
            self.topic, self.payload_str, qos=1
        )

    def test_fail_connect(self):
        self.mock_mqtt_client.connect.side_effect = OSError("could not connect")
        with pytest.raises(OSError) as ex:
            self.mqtt_writer.publish(self.topic, self.payload)
        assert "Cannot connect to MQTT broker" in str(ex.value)
