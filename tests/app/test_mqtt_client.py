"""Unit tests for the MqttClient class in the app.mqtt_client module."""

import unittest
from unittest.mock import MagicMock
import paho.mqtt.client as mqtt
from app.mqtt_client import MqttClient


class TestMqttClient(unittest.TestCase):
    def setUp(self):
        self.mock_mqtt_client = MagicMock(spec=mqtt.Client)
        self.mqtt_client = MqttClient(
            port=1883, host="localhost", client=self.mock_mqtt_client
        )

    def test_run(self):
        # Assume connect method always successful
        self.mock_mqtt_client.connect.return_value = 0

        # Run the method
        self.mqtt_client.run()

        # Verify that connect was called with the correct parameters
        self.mock_mqtt_client.connect.assert_called_with("localhost", 1883)


if __name__ == "__main__":
    unittest.main()
