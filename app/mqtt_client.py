import paho.mqtt.client as mqtt


def _decode_message(message):
    return message.payload.decode()


class MqttClient:
    _client: mqtt.Client

    def __init__(self, port: int, host: str, client: mqtt.Client) -> None:
        self._client = client
        self.host = host
        self.port = port
        self.on_message_callbacks = []
        self.topics = []

    def subscribe_topics(self, topics: list[str]):
        for topic in topics:
            self.topics.append(topic)

    def add_message_callback(self, f):
        self.on_message_callbacks.append(f)

    def run(self) -> None:
        """
        this is a blocking operation.
        """
        self._client.on_connect = self._on_connect()
        self._client.on_message = self._on_message()

        try:
            self._client.connect(self.host, self.port)
        except OSError as e:
            raise OSError(
                f"Cannot assign requested address: {self.host}:{self.port}"
            ) from e

        self._client.loop_forever()

    def _on_connect(self):
        def inner(client, _userdata, _flags, rc):
            if rc == 0:
                print("Connected to MQTT broker")
                for topic in self.topics:
                    client.subscribe(topic)
            else:
                print("Connection failed")

        return inner

    def _on_message(self):
        def inner(_client, _userdata, message):
            msg = _decode_message(message)
            for callback in self.on_message_callbacks:
                callback(msg)

        return inner
