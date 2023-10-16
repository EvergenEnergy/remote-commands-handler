"""Tests for the Configuration module."""
import os
from copy import deepcopy

import pytest
from pymodbus.constants import Endian

import app.configuration
from app.configuration import (
    Coil,
    Configuration,
    HoldingRegister,
    ModbusSettings,
    MqttSettings,
    SiteSettings,
    InputTypes,
    path_to_yaml_data,
    _validate_config,
    _mqtt_settings_from_yaml_data,
)
from app.exceptions import ConfigurationFileNotFoundError, ConfigurationFileInvalidError


def _config_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "example_configuration.yaml")
    return config_path


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
    assert evg_battery_mode_coil_address.input_type == InputTypes.COIL
    assert target_watt_coil.input_type == InputTypes.COIL


def test_get_holding_registers():
    configuration = Configuration.from_file(_config_path())

    evg_battery_mode = configuration.get_holding_register("evgBatteryMode")

    assert evg_battery_mode.name == "evgBatteryMode"
    assert evg_battery_mode.memory_order.order() == (Endian.Big, Endian.Big)
    assert evg_battery_mode.data_type == "INT16"
    assert evg_battery_mode.scale == 1.0
    assert evg_battery_mode.address == [0]
    assert evg_battery_mode.input_type == InputTypes.REGISTER

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
    assert evg_battery_target_soc_percent.input_type == InputTypes.REGISTER


def test_able_to_get_mqtt_settings():
    configuration = Configuration.from_file(_config_path())

    mqtt_settings = configuration.get_mqtt_settings()

    assert mqtt_settings.port == 9000
    assert mqtt_settings.host == "mqtt.host"
    assert mqtt_settings.command_topic == "commands/#"
    assert mqtt_settings.pub_errors is True

    config = path_to_yaml_data(_config_path())

    no_err_topic = deepcopy(config)
    del no_err_topic["mqtt_settings"]["error_topic"]
    new_mqtt_settings = _mqtt_settings_from_yaml_data(no_err_topic)
    assert new_mqtt_settings.pub_errors is False

    empty_err_topic = deepcopy(config)
    empty_err_topic["mqtt_settings"]["error_topic"] = ""
    new_mqtt_settings = _mqtt_settings_from_yaml_data(empty_err_topic)
    assert new_mqtt_settings.pub_errors is False


def test_able_to_get_modbus_settings():
    configuration = Configuration.from_file(_config_path())

    modbus_settings = configuration.get_modbus_settings()

    assert modbus_settings.port == 8080
    assert modbus_settings.host == "modbus.host"


def test_able_to_get_site():
    configuration = Configuration.from_file(_config_path())

    site_settings = configuration.get_site_settings()

    assert site_settings.site_name == "testsite"
    assert site_settings.serial_number == "testserial"


def test_get_coils():
    coils = [Coil("test_coil", 1)]
    holding_registers = []
    mqtt_settings = MqttSettings("test", 100, "test")
    modbus_settings = ModbusSettings("localhost", 10)
    site_settings = SiteSettings("testsite", "testdevice")
    configuration = Configuration(
        coils, holding_registers, mqtt_settings, modbus_settings, site_settings
    )

    assert coils == configuration.get_coils()


def test_get_registers():
    coils = []
    holding_registers = [HoldingRegister("test", "AB", "STR", 1.0, [0])]
    mqtt_settings = MqttSettings("test", 100, "test")
    modbus_settings = ModbusSettings("localhost", 10)
    site_settings = SiteSettings("testsite", "testdevice")
    configuration = Configuration(
        coils, holding_registers, mqtt_settings, modbus_settings, site_settings
    )

    assert holding_registers == configuration.get_holding_registers()


def test_validate_config_data():
    config = path_to_yaml_data(_config_path())

    for key in ("modbus_settings", "mqtt_settings", "modbus_mapping"):
        c = deepcopy(config)

        c[key] = ["is a list", "not a dict"]
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _validate_config(c)
        assert key in str(ex.value)

        del c[key]
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _validate_config(c)
        assert key in str(ex.value)

        if key != "modbus_mapping":
            c = deepcopy(config)

            c[key]["host"] = ""
            with pytest.raises(ConfigurationFileInvalidError) as ex:
                _validate_config(c)
            assert "host" in str(ex.value)
            assert key in str(ex.value)

            del c[key]["host"]
            with pytest.raises(ConfigurationFileInvalidError) as ex:
                _validate_config(c)
            assert "host" in str(ex.value)
            assert key in str(ex.value)

    without_error_topic = deepcopy(config)
    del without_error_topic["mqtt_settings"]["error_topic"]
    try:
        _validate_config(without_error_topic)
    except Exception:
        assert False

    error_topic_wildcard = deepcopy(config)
    for char in ("#", "+"):
        error_topic_wildcard["mqtt_settings"]["error_topic"] = f"error/{char}/topic"
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _validate_config(error_topic_wildcard)
        assert "wildcard" in str(ex.value)

    for datatype in ("coils", "holding_registers"):
        c = deepcopy(config)
        del c["modbus_mapping"][datatype][0]["address"]
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _validate_config(c)
        assert "address" in str(ex.value)

    for datatype in ("coils", "holding_registers"):
        c = deepcopy(config)
        del c["modbus_mapping"][datatype]
        _validate_config(c)


def test_key_error_in_config_parsing(monkeypatch):
    """
    Test that if the config module looks for a dict key which isn't set in the file,
    we capture that error in a custom exception
    """

    def modbus_settings_with_unknown_key(data):
        return ModbusSettings(data["not_host_key"], data["not_port"])

    def modbus_settings_with_bad_type(data):
        settings = [1, 2, 3]
        return ModbusSettings(settings["host"], settings["port"])

    with monkeypatch.context() as m:
        m.setattr(
            app.configuration,
            "_modbus_settings_from_yaml_data",
            modbus_settings_with_unknown_key,
        )
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _ = Configuration.from_file(_config_path())
        assert "Error parsing configuration" in str(ex.value)
        assert "not_host_key" in str(ex.value)

        m.setattr(
            app.configuration,
            "_modbus_settings_from_yaml_data",
            modbus_settings_with_bad_type,
        )
        with pytest.raises(ConfigurationFileInvalidError) as ex:
            _ = Configuration.from_file(_config_path())
        assert "Error parsing configuration" in str(ex.value)


def test_read_settings_from_env():
    env_var_path = _config_path().replace("example", "good_env_var")
    with pytest.raises(ConfigurationFileInvalidError) as ex:
        _ = Configuration.from_file(env_var_path)
    assert (
        str(ex.value)
        == "Missing value for expected environment variable 'SITE_NAME' in config"  # noqa
    )

    os.environ["SITE_NAME"] = "site-from-env"
    os.environ["SERIAL_NUMBER"] = "serial-from-env"
    config = Configuration.from_file(env_var_path)
    assert config.get_site_settings().site_name == "site-from-env"
    assert config.get_site_settings().serial_number == "serial-from-env"
    assert (
        config.get_mqtt_settings().error_topic
        == "telemetry/site-from-env/error/serial-from-env/site-from-env"  # noqa
    )
    os.environ["SITE_NAME"] = ""
    os.environ["SERIAL_NUMBER"] = ""
