"""Unit tests for the ModbusClient class in the app.modbus_client module."""

from unittest.mock import MagicMock
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from app.memory_order import MemoryOrder
from app.modbus_client import ModbusClient
from app.payload_builder import PayloadBuilder
from app.configuration import Coil, Configuration, ModbusSettings, HoldingRegister
from app.error_handler import ErrorHandler
from app.exceptions import UnknownCommandError, ModbusClientError, InvalidMessageError
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
        self.mock_error_handler = MagicMock(spec=ErrorHandler)

        configuration = Configuration(
            self.coils, self.holding_registers, {}, self.modbus_settings
        )

        self.modbus_client = ModbusClient(
            configuration,
            self.mock_error_handler,
            modbus_client=self.mock_client,
        )

    @pytest.mark.parametrize("coil_value", [False, True])
    def test_coils(self, coil_value):
        coil_list = [coil_value] * 2
        for coil in self.coils:
            sent = self.modbus_client.write_coil(coil.name, coil_value)
            self.mock_client.write_coil.assert_called_with(
                coil.address[0], coil_value, 1
            )
            assert sent == 1

            sent = self.modbus_client.write_coils(coil.name, coil_list)
            self.mock_client.write_coils.assert_called_with(coil.address[0], coil_list)
            assert sent == 2

        assert self.modbus_client.write_coil("bad_coil", coil_value) == 0
        assert self.modbus_client.write_coils("bad_coil", coil_list) == 0

    def test_registers(self):
        for register in self.holding_registers:
            if "INT" in register.data_type:
                value = 10
            elif "FLOAT" in register.data_type:
                value = 32.3
            sent = self.modbus_client.write_register(register.name, value)
            assert sent == 1
        assert self.mock_client.write_registers.call_count == len(
            self.holding_registers
        )

        assert self.modbus_client.write_register("bad_register", 54) == 0

    def test_write_command(self):
        test_register = self.holding_registers[0]
        self.modbus_client.write_command(test_register.name, 0)
        self.mock_client.write_registers.assert_called_with(1, [0], 1)

        test_coil = self.coils[0]
        self.modbus_client.write_command(test_coil.name, True)
        self.mock_client.write_coil.assert_called_with(1, True, 1)

        with pytest.raises(UnknownCommandError) as ex:
            assert self.modbus_client.write_command("bad_register", 54) == 0
        assert "bad_register" in str(ex.value)
        self.mock_error_handler.publish.assert_called_once()

    def test_connect_failure(self):
        self.mock_client.connect.side_effect = ModbusException("could not connect")
        test_coil = self.coils[0]
        with pytest.raises(ModbusClientError) as ex:
            self.modbus_client.write_coil(test_coil.name, True)
        assert "could not connect" in str(ex.value)

        with pytest.raises(ModbusClientError) as ex:
            self.modbus_client.write_coils(test_coil.name, [True, False])
        assert "could not connect" in str(ex.value)

        test_register = self.holding_registers[0]
        with pytest.raises(ModbusClientError) as ex:
            self.modbus_client.write_command(test_register.name, 0)
        assert "could not connect" in str(ex.value)

        self.mock_client.connect.side_effect = None

    def test_bad_payload(self, monkeypatch):
        def fake_build(_):
            raise RuntimeError("nope")

        with monkeypatch.context() as m:
            m.setattr(
                PayloadBuilder,
                "build",
                fake_build,
            )
            test_register = self.holding_registers[0]
            with pytest.raises(InvalidMessageError) as ex:
                self.modbus_client.write_command(test_register.name, 0)
            assert ex.type == InvalidMessageError
