import logging

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
            logging.debug("wrote to coils: %s, values: %s", name, value)
        except KeyError:
            logging.error("unknown action: %s", name)

    def write_coil(self, name: str, value: bool):
        try:
            coil_configuration = self.configuration.get_coil(name)
            self._client.connect()
            self._client.write_coil(coil_configuration.address[0], value, 1)
            self._client.close()
            logging.debug("wrote to coil: %s, value: %s", name, value)
        except KeyError:
            logging.error("unknown action: %s", name)

    def write_register(self, name: str, value):
        try:
            holding_register_configuration = self.configuration.get_holding_register(
                name
            )
            self._client.connect()
            self._client.write_register(
                holding_register_configuration.address[0], value, 1
            )
            self._client.close()
            logging.debug("wrote to register %s, value: %s", name, value)
        except KeyError:
            logging.error("unknown action: %s", name)
