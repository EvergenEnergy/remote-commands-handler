"""Tests for the Configuration module."""
import os
from copy import deepcopy

import pytest
from pymodbus.constants import Endian

from app.configuration import (
    Coil,
    Configuration,
    HoldingRegister,
    ModbusSettings,
    MqttSettings,
    path_to_yaml_data,
    _validate_config,
)
from app.exceptions import ConfigurationFileNotFoundError, ConfigurationFileInvalidError


def test_throws_exception_when_configuration_file_not_found():
    with pytest.raises(ConfigurationFileNotFoundError):
        Configuration.from_file("./tests/config/bad-example_configuration.yaml")


def test_throws_exception_when_configuration_file_has_syntax_errors():
    bad_yaml_path = "/tmp/bad.yaml"
    with open(bad_yaml_path, "w") as bad:
        bad.write("not:\nvalid")
    with pytest.raises(ConfigurationFileInvalidError) as ex:
        Configuration.from_file(bad_yaml_path)
    assert "Error encountered parsing YAML" in str(ex.value)
    os.remove(bad_yaml_path)


def test_get_coil():
    configuration = Configuration.from_file(_config_path())

    evg_battery_mode_coil_address = configuration.get_coil("evgBatteryModeCoil")
    target_watt_coil = configuration.get_coil("evgBatteryTargetPowerWattsCoil")

    assert evg_battery_mode_coil_address.address == [3]
    assert target_watt_coil.address == [4]


def _config_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "example_configuration.yaml")
    return config_path


def test_get_holding_registers():
    configuration = Configuration.from_file(_config_path())

    evg_battery_mode = configuration.get_holding_register("evgBatteryMode")

    assert evg_battery_mode.name == "evgBatteryMode"
    assert evg_battery_mode.memory_order.order() == (Endian.Big, Endian.Big)
    assert evg_battery_mode.data_type == "INT16"
    assert evg_battery_mode.scale == 1.0
    assert evg_battery_mode.address == [0]

    evg_battery_target_soc_percent = configuration.get_holding_register(
        "evgBatteryTargetSOCPercent"
    )

    assert evg_battery_target_soc_percent.name == "evgBatteryTargetSOCPercent"
    assert evg_battery_target_soc_percent.memory_order.order() == (
        Endian.Big,
        Endian.Big,
    )
    assert evg_battery_target_soc_percent.data_type == "INT16"
    assert evg_battery_target_soc_percent.scale == 1.0
    assert evg_battery_target_soc_percent.address == [2]


def test_able_to_get_mqtt_settings():
    configuration = Configuration.from_file(_config_path())

    mqtt_settings = configuration.get_mqtt_settings()

    assert mqtt_settings.port == 9000
    assert mqtt_settings.host == "mqtt.host"
    assert mqtt_settings.command_topic == "commands/#"


def test_able_to_get_modbus_settings():
    configuration = Configuration.from_file(_config_path())

    modbus_settings = configuration.get_modbus_settings()

    assert modbus_settings.port == 8080
    assert modbus_settings.host == "modbus.host"


def test_get_coils():
    coils = [Coil("test_coil", 1)]
    holding_registers = []
    mqtt_settings = MqttSettings("test", 100, "test")
    modbus_settings = ModbusSettings("localhost", 10)
    configuration = Configuration(
        coils, holding_registers, mqtt_settings, modbus_settings
    )

    assert coils == configuration.get_coils()


def test_get_registers():
    coils = []
    holding_registers = [HoldingRegister("test", "AB", "STR", 1.0, [0])]
    mqtt_settings = MqttSettings("test", 100, "test")
    modbus_settings = ModbusSettings("localhost", 10)
    configuration = Configuration(
        coils, holding_registers, mqtt_settings, modbus_settings
    )

    assert holding_registers == configuration.get_holding_registers()


def test_validate_config_data():
    config = path_to_yaml_data(_config_path())

    for key in ("modbus_settings", "mqtt_settings", "modbus_mapping"):
        c = deepcopy(config)
        del c[key]
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _validate_config(c)
        assert key in str(ex.value)

        if key != "modbus_mapping":
            c = deepcopy(config)
            del c[key]["host"]
            with pytest.raises(ConfigurationFileInvalidError) as ex:
                _validate_config(c)
            assert "host" in str(ex.value)
            assert key in str(ex.value)

    for datatype in ("coils", "holding_registers"):
        c = deepcopy(config)
        del c["modbus_mapping"][datatype][0]["address"]
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _validate_config(c)
        assert "address" in str(ex.value)
