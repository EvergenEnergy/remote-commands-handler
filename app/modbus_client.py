from pymodbus.client import ModbusTcpClient
from app.configuration import Configuration

class ModbusClient:
    def __init__(self, configuration: Configuration, port: int, host: str) -> None:
        self.configuration = configuration 
        self.client = ModbusTcpClient(host, port=port)

    def write_coils(self, name: str, value: list[bool]):
        coil_configuration = self.configuration.get_coil(name)
        self.client.connect()
        self.client.write_coils(coil_configuration.address, value)
        self.client.close()

    def write_coil(self, name: str, value: bool):
        coil_configuration = self.configuration.get_coil(name)
        self.client.connect()
        self.client.write_coil(coil_configuration.address, value)
        self.client.close()
    
    def write_register(self, name: str, value):
        holding_register_configuration = self.configuration.get_holding_register(name)
        self.client.connect()
        self.client.write_register(holding_register_configuration.address, value)
        self.client.close()