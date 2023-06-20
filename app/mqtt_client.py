"""MQTT Client module.

This module provides a client class for interacting with MQTT brokers. It allows subscribing to topics,
adding message callbacks, and running the client to establish and maintain a connection to the broker.

The main class in this module is `MqttClient`, which encapsulates the functionality of the MQTT client.

Example:
    Instantiate an `MqttClient` object and run it:

    ```
    client = MqttClient(port=1883, host="localhost", client=mqtt.Client())
    client.subscribe_topics(["topic1", "topic2"])
    client.add_message_callback(my_callback_function)
    client.run()
    ```

Note:
    This module requires the `paho-mqtt` package to be installed.

"""

import paho.mqtt.client as mqtt


class MqttClient:
    _client: mqtt.Client

    def __init__(
        self,
        host: str,
        port: int,
        client: mqtt.Client = None,
    ):
        self.host = host
        self.port = port
        self._client = client or mqtt.Client()

    def connect(self) -> None:
        try:
            self._client.connect(self.host, self.port)
            return True
        except OSError as e:
            ex = OSError(f"Cannot assign requested address: {self.host}:{self.port}")
            raise ex from e
