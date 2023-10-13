"""Unit tests for the ModbusClient class in the app.modbus_client module."""

from unittest.mock import MagicMock
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from app.memory_order import MemoryOrder
from app.message import CommandMessage
from app.modbus_client import ModbusClient
from app.configuration import (
    Coil,
    Configuration,
    ModbusSettings,
    HoldingRegister,
    SiteSettings,
)
from app.error_handler import ErrorHandler
from app.exceptions import ModbusClientError
import pytest


class MockModbusResponse:
    def isError(self):
        return False


class TestModbusClient:
    def setup_method(self):
        self.coils = [Coil("test_coil", [1])]
        self.holding_registers = [
            HoldingRegister("int_register", MemoryOrder("AB"), "INT16", 1.0, [1]),
            HoldingRegister(
                "float_register", MemoryOrder("BA"), "FLOAT32-IEEE", 1.0, [1]
            ),
        ]
        self.site_settings = SiteSettings("localhost", "DEV123")
        self.modbus_settings = ModbusSettings("localhost", 5020)
        self.mock_client = MagicMock(spec=ModbusTcpClient)
        self.mock_client.write_coil.return_value = MockModbusResponse()
        self.mock_client.write_coils.return_value = MockModbusResponse()
        self.mock_client.write_registers.return_value = MockModbusResponse()
        self.mock_error_handler = MagicMock(spec=ErrorHandler)

        self.configuration = Configuration(
            self.coils,
            self.holding_registers,
            {},
            self.modbus_settings,
            self.site_settings,
        )

        self.modbus_client = ModbusClient(
            self.configuration,
            self.mock_client,
            self.mock_error_handler,
        )

    @pytest.mark.parametrize("coil_value", [False, True])
    def test_coils(self, coil_value):
        coil_list = [coil_value] * 2
        for coil in self.coils:
            msg = CommandMessage(coil.name, coil_value, self.configuration)
            sent = self.modbus_client.write_command(msg)
            self.mock_client.write_coil.assert_called_with(
                coil.address[0], coil_value, 1
            )
            assert sent == 1

            msg = CommandMessage(coil.name, coil_list, self.configuration)
            sent = self.modbus_client.write_command(msg)
            self.mock_client.write_coils.assert_called_with(coil.address[0], coil_list)
            assert sent == 2

    def test_registers(self):
        for register in self.holding_registers:
            if "INT" in register.data_type:
                value = 10
            elif "FLOAT" in register.data_type:
                value = 32.3
            sent = self.modbus_client.write_command(
                CommandMessage(register.name, value, self.configuration)
            )
            assert sent == 1
        assert self.mock_client.write_registers.call_count == len(
            self.holding_registers
        )

    def test_write_command(self):
        test_register = self.holding_registers[0]
        self.modbus_client.write_command(
            CommandMessage(test_register.name, 0, self.configuration)
        )
        self.mock_client.write_registers.assert_called_with(1, [0], 1)

        test_coil = self.coils[0]
        self.modbus_client.write_command(
            CommandMessage(test_coil.name, True, self.configuration)
        )
        self.mock_client.write_coil.assert_called_with(1, True, 1)

    def test_connect_failure(self):
        self.mock_client.connect.side_effect = ModbusException("could not connect")
        test_coil = self.coils[0]
        with pytest.raises(ModbusClientError) as ex:
            self.modbus_client._write_coil(test_coil.name, True)
        assert "could not connect" in str(ex.value)

        with pytest.raises(ModbusClientError) as ex:
            self.modbus_client._write_coils(test_coil.name, [True, False])
        assert "could not connect" in str(ex.value)

        test_register = self.holding_registers[0]
        with pytest.raises(ModbusClientError) as ex:
            self.modbus_client._write_register(test_register.name, 0)
        assert "could not connect" in str(ex.value)

        self.modbus_client.write_command(
            CommandMessage(test_coil.name, True, self.configuration)
        )
        self.mock_error_handler.publish.assert_called_with(
            self.mock_error_handler.Category.MODBUS_ERROR,
            "Modbus Error: could not connect",
        )
        self.mock_client.connect.side_effect = None

    def test_bad_payload(self):
        # Create a new modbus client with a holding register that has an invalid datatype
        holding_reg = HoldingRegister(
            "int_register", MemoryOrder("AB"), "FOO", 1.0, [1]
        )
        new_config = Configuration(
            self.coils,
            [holding_reg],
            {},
            self.modbus_settings,
            self.site_settings,
        )
        modbus_client = ModbusClient(
            new_config,
            self.mock_client,
            self.mock_error_handler,
        )
        test_register = self.holding_registers[0]
        modbus_client.write_command(
            CommandMessage(test_register.name, 0, self.configuration)
        )
        self.mock_error_handler.publish.assert_called_with(
            self.mock_error_handler.Category.INVALID_MESSAGE, "unknown data type FOO"
        )
