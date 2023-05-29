from pymodbus.client import ModbusTcpClient
from app.configuration import Configuration


class ModbusClient:
    _client: ModbusTcpClient

    def __init__(self, configuration: Configuration, port: int, host: str) -> None:
        self.configuration = configuration
        self._client = ModbusTcpClient(host, port=port)

    def write_coils(self, name: str, value: list[bool]):
        coil_configuration = self.configuration.get_coil(name)
        self._client.connect()
        self._client.write_coils(coil_configuration.address[0], value)
        self._client.close()

    def write_coil(self, name: str, value: bool):
        coil_configuration = self.configuration.get_coil(name)
        self._client.connect()
        self._client.write_coil(coil_configuration.address[0], value)
        self._client.close()

    def write_register(self, name: str, value):
        holding_register_configuration = self.configuration.get_holding_register(name)
        self._client.connect()
        self._client.write_register(holding_register_configuration.address[0], value)
        self._client.close()
