from pymodbus.client import ModbusTcpClient
from app.configuration import Configuration


class ModbusClient:
    _client: ModbusTcpClient

    def __init__(
        self, configuration: Configuration, modbus_client: ModbusTcpClient
    ) -> None:
        self.configuration = configuration
        self._client = modbus_client

    def write_coils(self, name: str, value: list[bool]):
        try:
            coil_configuration = self.configuration.get_coil(name)
            self._client.connect()
            self._client.write_coils(coil_configuration.address[0], value)
            self._client.close()
            print("wrote to coils", name, " value: ", value)
        except KeyError:
            print("unknown action: ", name)
            

    def write_coil(self, name: str, value: bool):
        try:
            coil_configuration = self.configuration.get_coil(name)
            self._client.connect()
            self._client.write_coil(coil_configuration.address[0], value, 1)
            test = self._client.read_coils(coil_configuration.address[0], 1, 1)
            print("test address: ", coil_configuration.address[0].as_integer_ratio())
            print("test value: ", test)
            self._client.close()
            print("wrote to coil", name, " value: ", value)
        except KeyError:
            print("unknown action: ", name)

    def write_register(self, name: str, value):
        try:
            holding_register_configuration = self.configuration.get_holding_register(name)
            self._client.connect()
            self._client.write_register(holding_register_configuration.address[0], value, 1)
            test = self._client.read_holding_registers(holding_register_configuration.address[0], 1, 1)
            print("test value: ", test)
            self._client.close()
            print("wrote to register", name, " value: ", value)
        except KeyError:
            print("unknown action: ", name)