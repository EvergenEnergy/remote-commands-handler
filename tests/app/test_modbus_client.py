"""Unit tests for the MqttClient class in the app.mqtt_client module."""

from unittest.mock import MagicMock
from pymodbus.client import ModbusTcpClient
from app.modbus_client import ModbusClient
from app.configuration import Coil, Configuration, ModbusSettings, HoldingRegister
from app.memory_order import MemoryOrder
import pytest


class TestModbusClient:
    def setup_class(self):
        self.coils = [Coil("test_coil", [1])]
        self.holding_registers = [
            HoldingRegister("int_register", MemoryOrder("AB"), "INT16", 1.0, [1]),
            HoldingRegister(
                "float_register", MemoryOrder("BA"), "FLOAT32-IEEE", 1.0, [1]
            ),
        ]
        self.modbus_settings = ModbusSettings("localhost", 5020)
        self.mock_client = MagicMock(spec=ModbusTcpClient)

        configuration = Configuration(
            self.coils, self.holding_registers, {}, self.modbus_settings
        )

        self.modbus_client = ModbusClient(configuration, self.mock_client)

    @pytest.mark.parametrize("coil_value", [False, True])
    def test_coils(self, coil_value, caplog):
        coil_list = [coil_value] * 2
        for coil in self.coils:
            self.modbus_client.write_coil(coil.name, coil_value)
            self.mock_client.write_coil.assert_called_with(
                coil.address[0], coil_value, 1
            )

            self.modbus_client.write_coils(coil.name, coil_list)
            self.mock_client.write_coils.assert_called_with(coil.address[0], coil_list)

        self.modbus_client.write_coil("bad_coil", coil_value)
        assert "unknown action" in str(caplog.records[-1])
        self.modbus_client.write_coils("bad_coil", coil_list)
        assert "unknown action" in str(caplog.records[-1])

    def test_registers(self, caplog):
        for register in self.holding_registers:
            if "INT" in register.data_type:
                value = 10
            elif "FLOAT" in register.data_type:
                value = 32.3
            self.modbus_client.write_register(register.name, value)
        assert self.mock_client.write_registers.call_count == len(
            self.holding_registers
        )

        self.modbus_client.write_register("bad_register", 54)
        assert "unknown action" in str(caplog.records[-1])
